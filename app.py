#Streamlit interface for interacting with the application


# Libraries import

import streamlit as st
import time
from llm_parser import parse_problem
from template_engine import build_case
from foam_runner import run_simulation
from visualizer import render_results

st.set_page_config(page_title="FluidAI", layout="wide")
st.title("FluidAI — Natural Language CFD")


# Defining session state

if "params" not in st.session_state:
    st.session_state.params = None
if "case_dir" not in st.session_state:
    st.session_state.case_dir = None
if "log" not in st.session_state:
    st.session_state.log = ""


# Sidebar configuration

with st.sidebar:
    st.header("Config")
    llm_backend = st.selectbox("LLM backend", ["groq", "ollama", "gemini"])
    if llm_backend == "groq":
        api_key = st.text_input("Groq API key", type="password")
    elif llm_backend == "gemini":
        api_key = st.text_input("Gemini API key", type="password")
    else:
        api_key = None
        st.info("Ollama runs locally — no key needed")
    max_cells = st.slider("Max mesh cells (k)", 50, 500, 200) * 1000
    wall_time  = st.slider("Max wall time (min)", 1, 10, 5)
    n_cores    = st.slider("CPU cores for OpenFOAM", 1, 12, 6)


# Problem input

col1, col2 = st.columns([2, 1])

with col1:
    problem = st.text_area(
        "Describe your fluid dynamics problem",
        placeholder="e.g. Turbulent airflow over a backward facing step at Re=5000, "
                    "air at 20°C, inlet velocity 10 m/s",
        height=120,
    )

with col2:
    st.markdown("**Example problems**")
    examples = [
        "Laminar flow in a 2D cavity, Re=100",
        "Turbulent pipe flow, water, Re=10000",
        "Channel flow between parallel plates, Re=500",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state["problem_prefill"] = ex

if "problem_prefill" in st.session_state:
    problem = st.session_state.pop("problem_prefill")

# Parse the problem and create JSON file

if st.button("Parse problem", disabled=not problem):
    with st.spinner("Asking LLM to decode problem…"):
        params, raw = parse_problem(problem, backend=llm_backend, api_key=api_key)
    if params:
        st.session_state.params = params
        st.success("Parsed successfully")
        with st.expander("Raw JSON from LLM"):
            st.json(raw)
    else:
        st.error("Parse failed. Try rephrasing or check API key")


# Show or edit params

if st.session_state.params:
    p = st.session_state.params
    st.subheader("Simulation parameters")
    cols = st.columns(4)
    p["solver"]     = cols[0].selectbox("Solver", ["icoFoam","simpleFoam","pisoFoam"], index=["icoFoam","simpleFoam","pisoFoam"].index(p.get("solver","simpleFoam")))
    p["template"]   = cols[1].selectbox("Template", ["cavity","pipeFlow","channel"], index=["cavity","pipeFlow","channel"].index(p.get("template","cavity")))
    p["nu"]         = cols[2].number_input("Kinematic viscosity ν (m²/s)", value=float(p.get("nu", 1e-5)), format="%.2e")
    p["U"]          = cols[3].number_input("Inlet velocity (m/s)", value=float(p.get("U", 1.0)))
    p["endTime"]    = st.number_input("End time (s)", value=float(p.get("endTime", 1.0)))
    p["n_cores"]    = n_cores
    p["max_cells"]  = max_cells
    st.session_state.params = p


# Run simulation

if st.session_state.params and st.button("Run simulation", type="primary"):
    p = st.session_state.params

    # Build case
    with st.spinner("Generating OpenFOAM case files…"):
        case_dir = build_case(p)
        st.session_state.case_dir = case_dir
    st.success(f"Case written to `{case_dir}`")

    # Stream simulation output
    st.subheader("Solver log")
    log_box = st.empty()
    log_lines = []
    deadline = time.time() + wall_time * 60

    for line in run_simulation(case_dir, p):
        log_lines.append(line)
        if time.time() > deadline:
            log_lines.append("⚠️  Wall-time limit reached — stopping")
            break
        log_box.code("".join(log_lines[-60:]), language="bash")

    st.session_state.log = "".join(log_lines)
    st.success("Simulation finished")


# Visualise results

if st.session_state.case_dir:
    st.subheader("Results")
    tab1, tab2, tab3 = st.tabs(["Velocity field", "Residuals", "Explain output"])

    with tab1:
        img = render_results(st.session_state.case_dir)
        if img:
            st.image(img, use_column_width=True)
        else:
            st.info("No VTK data found — did the solver finish?")

    with tab2:
        from visualizer import plot_residuals
        fig = plot_residuals(st.session_state.log)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        if st.button("Ask LLM to explain the log"):
            from llm_parser import explain_log
            with st.spinner("Analysing…"):
                explanation = explain_log(
                    st.session_state.log,
                    backend=llm_backend,
                    api_key=api_key,
                )
            st.markdown(explanation)
