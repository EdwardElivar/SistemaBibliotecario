from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "biblioteca.db"

def asset_path(*parts: str) -> Path:
    return BASE_DIR.joinpath("assets", *parts)
