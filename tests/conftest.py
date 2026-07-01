from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "sample_data"


@pytest.fixture
def sample_dir() -> Path:
    return SAMPLE


@pytest.fixture
def calc_dirs() -> dict[str, Path]:
    return {p.name: p for p in SAMPLE.iterdir() if (p / "invoer.hyd").exists()}
