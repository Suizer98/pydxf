import os

DATA_DIR = "data"


def ensure_data_dirs() -> None:
    """Create data/Files and data/Output if they do not exist."""
    os.makedirs(os.path.join(DATA_DIR, "Files"), exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, "Output"), exist_ok=True)
