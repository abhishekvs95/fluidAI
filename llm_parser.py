# Uses LLMs to decode natural language and produce validated JSON params
# Supports: groq, ollama, gemini (add other models if necessary)

#Calling Libraries

import json, re
from pydantic import BaseModel, validator, ValidationError
from typing import Literal, Optional


# OpenFOAM Schema

class FoamParams(BaseModel):
    solver:   Literal["icoFoam", "simpleFoam", "pisoFoam"] = "simpleFoam"
    template: Literal["cavity", "pipeFlow", "channel"]      = "cavity"
    nu:       float = 1e-5      # kinematic viscosity m²/s
    U:        float = 1.0       # inlet velocity m/s
    rho:      float = 1.0       # density kg/m³ (for reference)
    endTime:  float = 1.0       # simulation end time s
    deltaT:   float = 0.001     # time step s
    Re:       Optional[float] = None  # Reynolds number (informational)

    @validator("nu")
    def nu_positive(cls, v):
        if v <= 0:
            raise ValueError("nu must be positive")
        return v

    @validator("endTime")
    def endtime_positive(cls, v):
        if v <= 0:
            raise ValueError("endTime must be positive")
        return v


# System prompt definition

SYSTEM_PROMPT = """You are a CFD pre processor. The user describes a fluid dynamics problem in plain English.
Extract simulation parameters and return ONLY a JSON object (no prose, no markdown fences).

JSON keys (all required):
  solver   : one of "icoFoam" (laminar transient), "simpleFoam" (turbulent steady), "pisoFoam" (turbulent transient)
  template : one of "cavity" (lid-driven), "pipeFlow" (internal pipe), "channel" (parallel plates)
  nu       : kinematic viscosity in m²/s  (water ≈ 1e-6, air ≈ 1.5e-5)
  U        : inlet/lid velocity in m/s
  rho      : density in kg/m³ (water=1000, air=1.2)
  endTime  : simulation end time in seconds
  deltaT   : time-step in seconds
  Re       : Reynolds number if mentioned, else compute from U and geometry

Return ONLY JSON. Example:
{"solver":"simpleFoam","template":"cavity","nu":1.5e-5,"U":10.0,"rho":1.2,"endTime":2.0,"deltaT":0.005,"Re":5000}
"""


# Backend callers
def _call_groq(prompt: str, api_key: str) -> str:
    from groq import Groq
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        temperature=0,
        max_tokens=300,
    )
    return resp.choices[0].message.content


def _call_ollama(prompt: str, model: str = "mistral") -> str:
    import requests
    resp = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            "stream": False,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def _call_gemini(prompt: str, api_key: str) -> str:
    from google import genai
    client = genai.Client(api_key=api_key)
    full = f"{SYSTEM_PROMPT}\n\nUser: {prompt}"
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=full,
    )
    return response.text


# Public API

def parse_problem(
    problem: str,
    backend: str = "groq",
    api_key: str = None,
    max_retries: int = 2,
) -> tuple[Optional[dict], dict]:
    """
    Returns (validated_dict, raw_dict).
    On failure returns (None, {}).
    """
    raw_text = ""
    for attempt in range(max_retries):
        try:
            if backend == "groq":
                raw_text = _call_groq(problem, api_key)
            elif backend == "ollama":
                raw_text = _call_ollama(problem)
            elif backend == "gemini":
                raw_text = _call_gemini(problem, api_key)

            # Strip accidental markdown fences
            raw_text = re.sub(r"```[a-z]*", "", raw_text).strip("`\n ")

            raw_dict = json.loads(raw_text)
            params   = FoamParams(**raw_dict)
            return params.dict(), raw_dict

        except (json.JSONDecodeError, ValidationError, Exception) as e:
            if attempt == max_retries - 1:
                print(f"[llm_parser] Failed after {max_retries} attempts: {e}")
                return None, {}
            # Retry with error context
            problem = f"{problem}\n\nPrevious attempt failed: {e}. Fix and return only JSON."


def explain_log(log: str, backend: str = "groq", api_key: str = None) -> str:
    """Ask the LLM to interpret the OpenFOAM solver log."""
    prompt = (
        "You are a CFD expert. Analyse this OpenFOAM solver log. "
        "Explain convergence, any errors, and suggest fixes in ≤200 words.\n\n"
        f"LOG (last 100 lines):\n{log[-4000:]}"
    )
    try:
        if backend == "groq":
            return _call_groq(prompt, api_key)
        elif backend == "ollama":
            return _call_ollama(prompt)
        elif backend == "gemini":
            return _call_gemini(prompt, api_key)
    except Exception as e:
        return f"LLM call failed: {e}"
