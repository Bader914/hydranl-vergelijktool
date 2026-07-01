from pathlib import Path
import pandas as pd


def parse_ffq(path: Path) -> pd.DataFrame:
    """Lees ffq.txt: regel 1 = aantal, daarna paren (waterstand, frequentie)."""
    lines = Path(path).read_text(encoding="latin-1").split("\n")
    count = int(lines[0].strip())
    rows = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 2:
            rows.append((float(parts[0]), float(parts[1])))
    df = pd.DataFrame(rows, columns=["waterstand", "frequentie"])
    return df.head(count).reset_index(drop=True)
