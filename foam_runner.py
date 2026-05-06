"""
foam_runner.py — Run OpenFOAM pipeline, yield log lines for streaming
"""
import subprocess, shutil
from pathlib import Path
from typing import Generator


def _run_cmd(cmd: list[str], cwd: str) -> Generator[str, None, None]:
    """Run a shell command and yield stdout lines in real time."""
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    for line in proc.stdout:
        yield line
    proc.wait()
    if proc.returncode != 0:
        yield f"\n[ERROR] Command {' '.join(cmd)} exited with code {proc.returncode}\n"


def run_simulation(case_dir: str, params: dict) -> Generator[str, None, None]:
    """
    Full pipeline:
      1. blockMesh
      2. (optional) decomposePar  if n_cores > 1
      3. solver
      4. (optional) reconstructPar
    Yields log lines for live display.
    """
    n = params.get("n_cores", 1)
    solver = params.get("solver", "simpleFoam")

    # Verify OpenFOAM is available
    if not shutil.which("blockMesh"):
        yield "[ERROR] OpenFOAM not found on PATH. Source /opt/openfoam*/etc/bashrc first.\n"
        return

    yield "=== blockMesh ===\n"
    yield from _run_cmd(["blockMesh"], cwd=case_dir)

    if n > 1:
        _write_decompose_dict(case_dir, n)
        yield f"\n=== decomposePar ({n} cores) ===\n"
        yield from _run_cmd(["decomposePar"], cwd=case_dir)
        yield f"\n=== {solver} (parallel) ===\n"
        yield from _run_cmd(
            ["mpirun", "-np", str(n), solver, "-parallel"],
            cwd=case_dir,
        )
        yield "\n=== reconstructPar ===\n"
        yield from _run_cmd(["reconstructPar"], cwd=case_dir)
    else:
        yield f"\n=== {solver} ===\n"
        yield from _run_cmd([solver], cwd=case_dir)

    yield "\n=== Done ===\n"


def _write_decompose_dict(case_dir: str, n: int):
    """Write system/decomposeParDict for scotch decomposition."""
    content = f"""FoamFile {{ version 2.0; format ascii; class dictionary;
    location "system"; object decomposeParDict; }}
numberOfSubdomains {n};
method          scotch;
"""
    path = Path(case_dir) / "system" / "decomposeParDict"
    path.write_text(content)
