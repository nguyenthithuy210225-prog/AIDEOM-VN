"""Project paths for local and Colab execution."""

from __future__ import annotations

import os
from pathlib import Path


def find_project_root() -> Path:
    """Return the project root, allowing override by AIDEOM_BASE_DIR."""
    env_base = os.environ.get("AIDEOM_BASE_DIR")
    if env_base:
        return Path(env_base).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


BASE_DIR = find_project_root()
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures"
REPORT_DIR = BASE_DIR / "reports"


def ensure_output_dirs() -> None:
    """Create output directories if they do not exist."""
    for path in (OUTPUT_DIR, TABLE_DIR, FIGURE_DIR, REPORT_DIR):
        path.mkdir(parents=True, exist_ok=True)
