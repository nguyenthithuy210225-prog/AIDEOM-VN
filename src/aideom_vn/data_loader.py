"""Data loading helpers for AIDEOM-VN exercises."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import DATA_DIR


REQUIRED_FILES = {
    "macro": "vietnam_macro_2020_2025.csv",
    "sectors": "vietnam_sectors_2024.csv",
    "regions": "vietnam_regions_2024.csv",
}


def data_path(filename: str, data_dir: Path = DATA_DIR) -> Path:
    """Return an absolute path to a data file."""
    return data_dir / filename


def require_file(filename: str, data_dir: Path = DATA_DIR) -> Path:
    """Return a data path and raise a useful error if it is missing."""
    path = data_path(filename, data_dir)
    if not path.exists():
        raise FileNotFoundError(
            f"Missing data file: {path}. Put the CSV into the data/ folder."
        )
    return path


def load_macro(data_dir: Path = DATA_DIR) -> pd.DataFrame:
    """Load Vietnam macro data for 2020-2025."""
    df = pd.read_csv(require_file(REQUIRED_FILES["macro"], data_dir))
    if "year" in df.columns:
        df = df.sort_values("year").reset_index(drop=True)
    return df


def load_sectors(data_dir: Path = DATA_DIR) -> pd.DataFrame:
    """Load Vietnam sector data for 2024."""
    return pd.read_csv(require_file(REQUIRED_FILES["sectors"], data_dir))


def load_regions(data_dir: Path = DATA_DIR) -> pd.DataFrame:
    """Load Vietnam regional data for 2024."""
    return pd.read_csv(require_file(REQUIRED_FILES["regions"], data_dir))


def check_data_files(data_dir: Path = DATA_DIR) -> pd.DataFrame:
    """Return a small status table for required input files."""
    rows = []
    for key, filename in REQUIRED_FILES.items():
        path = data_path(filename, data_dir)
        rows.append(
            {
                "dataset": key,
                "filename": filename,
                "exists": path.exists(),
                "path": str(path),
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(check_data_files().to_string(index=False))
