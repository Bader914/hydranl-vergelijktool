from pathlib import Path
import yaml

_PAD = Path(__file__).resolve().parent.parent / "data" / "parameters.yaml"


def laad_kennisbank(pad: Path = _PAD) -> dict:
    return yaml.safe_load(Path(pad).read_text(encoding="utf-8")) or {}


def beschrijf(key: str, kennis: dict) -> dict:
    info = kennis.get(key)
    if not info:
        return {"label": key, "uitleg": "", "eenheid": "", "impact": "onbekend"}
    return {
        "label": info.get("label", key),
        "uitleg": info.get("uitleg", ""),
        "eenheid": info.get("eenheid", ""),
        "impact": info.get("impact", "context"),
    }


def duid_waarde(key: str, waarde: str, kennis: dict) -> str:
    info = kennis.get(key) or {}
    waarden = info.get("waarden") or {}
    return waarden.get(str(waarde), str(waarde))
