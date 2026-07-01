from dataclasses import dataclass
from pathlib import Path
import pandas as pd

from .parse_invoer import parse_invoer
from .parse_ffq import parse_ffq
from .parse_uitvoer import (
    html_to_text, parse_metadata, parse_hbn_frequentie,
    parse_hbn_terugkeertijd, parse_illustratiepunten,
)


@dataclass
class Berekening:
    naam: str
    invoer: dict
    metadata: dict
    hbn_frequentie: pd.DataFrame
    hbn_terugkeertijd: pd.DataFrame
    illustratiepunten: list
    ffq: pd.DataFrame


def laad_berekening(map: Path) -> Berekening:
    map = Path(map)
    text = html_to_text(map / "uitvoer.html")
    return Berekening(
        naam=map.name,
        invoer=parse_invoer(map / "invoer.hyd"),
        metadata=parse_metadata(text),
        hbn_frequentie=parse_hbn_frequentie(text),
        hbn_terugkeertijd=parse_hbn_terugkeertijd(text),
        illustratiepunten=parse_illustratiepunten(text),
        ffq=parse_ffq(map / "ffq.txt") if (map / "ffq.txt").exists() else pd.DataFrame(),
    )
