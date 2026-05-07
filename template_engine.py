# This is a template filler: Fills OpenFOAM case templates from params dict

import os, shutil, tempfile
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent / "templates"


#Function to write template and replace all Jinja2 placeholers

def build_case(params: dict) -> str:
    template_name = params["template"]
    src = TEMPLATES_DIR / template_name
    if not src.exists():
        raise FileNotFoundError(f"Template '{template_name}' not found in {TEMPLATES_DIR}")

    # Fresh working directory
    case_dir = tempfile.mkdtemp(prefix=f"foam_{template_name}_")
    dst = Path(case_dir)

    # Copy tree
    shutil.copytree(src, dst, dirs_exist_ok=True)

    # Render every file with Jinja2
    env = Environment(loader=FileSystemLoader(str(dst)), keep_trailing_newline=True)
    for fpath in dst.rglob("*"):
        if fpath.is_file():
            rel = fpath.relative_to(dst).as_posix()
            try:
                tmpl    = env.get_template(rel)
                rendered = tmpl.render(**params)
                fpath.write_text(rendered)
            except Exception:
                pass  # Skip binary or non-template file 

    return case_dir
