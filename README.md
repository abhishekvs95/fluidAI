# FluidAI — NL CFD with OpenFOAM + LLM

## Setup

```bash
# 1. Install OpenFOAM (Ubuntu / WSL2)
sudo sh -c "wget -q -O - https://dl.openfoam.com/add-apt-repository | bash"
sudo apt install openfoam2312-default
echo "source /usr/lib/openfoam/openfoam2312/etc/bashrc" >> ~/.bashrc
source ~/.bashrc

# 2. Python env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

## LLM backends

| Backend | Free? | Setup |
|---------|-------|-------|
| Groq    | Yes (rate limited) | Get key at console.groq.com |
| Ollama  | Yes (local) | `ollama pull llama3` |
| Gemini Flash | Yes tier | Get key at aistudio.google.com |

## Adding templates

Copy `templates/cavity/` → `templates/myCase/`  
Use `{{ nu }}`, `{{ U }}`, `{{ endTime }}` etc. as Jinja2 placeholders.  
Add the name to the `template` literal in `llm_parser.py`.

## Hardware notes (Ryzen 5 3600 / 32 GB / GTX 1060)

- Set n_cores = 6 for best performance (6 physical cores)
- Keep mesh cells < 300 k for < 2 min turnaround
- GTX 1060 used only for PyVista rendering (no OpenFOAM GPU support)
- For headless rendering: `sudo apt install xvfb`
