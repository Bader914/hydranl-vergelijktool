import re
from pathlib import Path
import pandas as pd


def html_to_text(path: Path) -> str:
    html = Path(path).read_text(encoding="latin-1")
    return re.sub(r"<[^>]+>", "", html)


def parse_metadata(text: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    patterns = {
        "locatie": r"^Locatie\s*=\s*(\S+)",
        "x": r"X-co.rdinaat\s*=\s*(\d+)",
        "y": r"Y-co.rdinaat\s*=\s*(\d+)",
        "datum": r"Datum berekening\s*=\s*(.+)",
        "versie": r"Versienummer:\s*(\S+)",
        "kritiek_overslagdebiet": r"Kritiek overslagdebiet\s*=\s*([\d.]+)",
    }
    for key, pat in patterns.items():
        m = re.search(pat, text, re.MULTILINE)
        if m:
            meta[key] = m.group(1).strip()
    return meta


def parse_hbn_frequentie(text: str) -> pd.DataFrame:
    rows = []
    for m in re.finditer(r"^\s*1/\s*(\d+)\s+([\d.]+)", text, re.MULTILINE):
        rows.append((int(m.group(1)), float(m.group(2))))
    return pd.DataFrame(rows, columns=["frequentie", "hbn"])


def parse_hbn_terugkeertijd(text: str) -> pd.DataFrame:
    # Blok tussen de kop 'Terugkeertijd ... belastingniveau' en de lege regel erna.
    m = re.search(
        r"Terugkeertijd\s+Hydraulisch belastingniveau.*?\n\s*\(jaren\).*?\n(.*?)\n\s*\n",
        text, re.DOTALL,
    )
    rows = []
    if m:
        for line in m.group(1).split("\n"):
            parts = line.split()
            if len(parts) == 2:
                rows.append((int(parts[0]), float(parts[1])))
    return pd.DataFrame(rows, columns=["terugkeertijd", "hbn"])


_KOLOMMEN = [
    "windrichting", "zeews", "q_rijn", "q_maas", "windsn",
    "h_teen", "hm0", "tm", "golfr", "ov_freq", "ov_pct",
]


def _cel(waarde: str):
    waarde = waarde.strip()
    if waarde in ("", "--"):
        return None
    try:
        return int(waarde) if re.fullmatch(r"-?\d+", waarde) else float(waarde)
    except ValueError:
        return waarde


def parse_illustratiepunten(text: str) -> list[dict]:
    blokken = []
    kop = re.compile(
        r"Illustratiepunten bij hydraulisch belastingniveau\s+([\d.]+).*?"
        r"terugkeertijd\s+(\d+)",
    )
    matches = list(kop.finditer(text))
    for i, m in enumerate(matches):
        start = m.end()
        einde = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        blok = text[start:einde]
        tabellen = []
        # Sub-tabellen beginnen bij een toestand-regel (Geopende/Gesloten ...);
        # daarna volgen kopregels en pas daarna de windrichting-datarijen.
        toestand_koppen = list(re.finditer(r"^(Geopende|Gesloten)[^\n]*", blok, re.MULTILINE))
        for j, tk in enumerate(toestand_koppen):
            seg_start = tk.end()
            seg_einde = toestand_koppen[j + 1].start() if j + 1 < len(toestand_koppen) else len(blok)
            segment = blok[seg_start:seg_einde]
            rijen = []
            for regel in segment.split("\n"):
                if "|" not in regel or "---" in regel:
                    continue
                cellen = [c.strip() for c in regel.split("|")]
                # Datarijen beginnen met een windrichting (hoofdletter N/O/Z/W).
                if not re.match(r"^[NOZW]{1,3}$", cellen[0]):
                    continue
                waarden = [cellen[0]] + [_cel(c) for c in cellen[1:]]
                rijen.append(waarden[: len(_KOLOMMEN)])
            if rijen:
                df = pd.DataFrame(rijen, columns=_KOLOMMEN[: len(rijen[0])])
                tabellen.append({"toestand": tk.group(0).strip(), "rijen": df})
        blokken.append({
            "hbn": float(m.group(1)),
            "terugkeertijd": int(m.group(2)),
            "tabellen": tabellen,
        })
    return blokken
