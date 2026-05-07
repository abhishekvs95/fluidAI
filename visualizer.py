# Render OpenFOAM results with Matplotlib (I'll update this file for the app to use pyvista for better rendering

#Calling Libraries

import re
from pathlib import Path
from typing import Optional
import plotly.graph_objects as go


# matplotlib renderer

def render_results(case_dir: str):
    import numpy as np
    import matplotlib.pyplot as plt
    import re, io, os

    time_dirs = sorted(
        [d for d in os.listdir(case_dir)
         if d.replace(".","").isdigit() and d != "0"],
        key=float
    )
    if not time_dirs:
        return None

    u_file = os.path.join(case_dir, time_dirs[-1], "U")
    if not os.path.exists(u_file):
        return None

    # This reads entire file and extract all (ux uy uz)  with regex
    content = open(u_file).read()
    vectors = re.findall(r'\(([+-]?[\d.eE+-]+)\s+([+-]?[\d.eE+-]+)\s+([+-]?[\d.eE+-]+)\)', content)

    # First match is often a boundary header therefore filter by keeping only internalField
    # Find count before the block
    count_match = re.search(r'internalField\s+nonuniform List<vector>\s+(\d+)', content)
    if not count_match:
        return None

    n_cells = int(count_match.group(1))
    # Take only the first n_cells vectors and skip boundary vectors at end
    internal = vectors[:n_cells]

    if not internal:
        return None

    mag = [( float(ux)**2 + float(uy)**2 + float(uz)**2 )**0.5
           for ux, uy, uz in internal]

    # Reshape because cavity mesh is 20x20 by default
    side = int(len(mag)**0.5)
    grid = np.array(mag[:side*side]).reshape(side, side)

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(grid, cmap="coolwarm", origin="lower")
    plt.colorbar(im, ax=ax, label="|U| m/s")
    ax.set_title(f"Velocity magnitude — t={time_dirs[-1]}s")
    ax.set_xlabel("x cells"); ax.set_ylabel("y cells")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(); buf.seek(0)
    return buf.read()

def _is_time_dir(name: str) -> bool:
    try:
        float(name)
        return True
    except ValueError:
        return False


# Residual plot: this fn parses openFOAM log for residuals and return a plotly figure
def plot_residuals(log: str) -> Optional[go.Figure]:
    pattern = re.compile(
        r"Solving for (\w+),\s+Initial residual = ([0-9eE+\-.]+)"
    )
    data: dict[str, list[float]] = {}
    for match in pattern.finditer(log):
        field, res = match.group(1), float(match.group(2))
        data.setdefault(field, []).append(res)

    if not data:
        return None

    fig = go.Figure()
    for field, residuals in data.items():
        fig.add_trace(go.Scatter(
            y=residuals,
            mode="lines",
            name=field,
        ))

    fig.update_layout(
        title="Solver residuals",
        xaxis_title="Iteration",
        yaxis_title="Residual",
        yaxis_type="log",
        template="plotly_white",
        height=350,
    )
    return fig
