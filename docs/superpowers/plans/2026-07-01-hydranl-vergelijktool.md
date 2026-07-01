# HydraNL Vergelijkingstool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Een Streamlit-tool die N HydraNL-berekeningen naast elkaar zet en in gewone taal invoerverschillen, HBN-resultaten en de impact daarvan uitlegt.

**Architecture:** Pure-Python bibliotheek `hydranl/` (parsers + vergelijk + kennisbank + duiding) die niets van Streamlit weet, met daarbovenop een dunne Streamlit-UI in `app.py`. Elke parser is een eigen module met eigen tests tegen de 3 meegeleverde berekeningen als fixtures.

**Tech Stack:** Python 3.11+, Streamlit, pandas, altair, rarfile (+ `unar` systeempakket), pyyaml, pytest.

## Global Constraints

- Python 3.11+; alle UI-teksten in het **Nederlands**.
- `hydranl/`-modules importeren **geen** streamlit.
- Parsers zijn defensief: missende velden, `--`-waarden en decimale komma/punt mogen niet crashen; onbekende parameters worden getoond zonder uitleg.
- Bestandscodering van `uitvoer.html` is `latin-1` (ISO-8859-1); altijd expliciet zo openen.
- Frequenties/HBN als floats; HBN-eenheid is m+NAP.
- Fixtures staan in `sample_data/{1_Shape_1,1_Shape_10,Def v01_Shape_1}/`.
- TDD: test eerst, dan implementatie; commit per taak.

---

### Task 1: Projectopzet en fixtures

**Files:**
- Create: `requirements.txt`, `packages.txt`, `.streamlit/config.toml`
- Create: `hydranl/__init__.py`
- Create: `tests/__init__.py`, `tests/conftest.py`
- Test: `tests/test_fixtures.py`

**Interfaces:**
- Produces: pytest-fixture `sample_dir` (Path naar `sample_data/`) en `calc_dirs` (dict naam→Path) voor alle latere tests.

- [ ] **Step 1: requirements.txt**

```
streamlit>=1.36
pandas>=2.0
altair>=5.0
rarfile>=4.1
pyyaml>=6.0
pytest>=8.0
```

- [ ] **Step 2: packages.txt** (Streamlit Cloud systeempakket voor RAR)

```
unar
```

- [ ] **Step 3: .streamlit/config.toml**

```toml
[theme]
primaryColor = "#0b5394"
base = "light"

[server]
maxUploadSize = 200
```

- [ ] **Step 4: hydranl/__init__.py** (leeg, maakt package)

```python
"""HydraNL vergelijk-bibliotheek: parsers, vergelijking en duiding."""
```

- [ ] **Step 5: tests/__init__.py** (leeg bestand)

```python
```

- [ ] **Step 6: tests/conftest.py**

```python
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
```

- [ ] **Step 7: tests/test_fixtures.py**

```python
def test_three_calculations_present(calc_dirs):
    assert set(calc_dirs) == {"1_Shape_1", "1_Shape_10", "Def v01_Shape_1"}
    for d in calc_dirs.values():
        assert (d / "invoer.hyd").exists()
        assert (d / "uitvoer.html").exists()
        assert (d / "ffq.txt").exists()
```

- [ ] **Step 8: Run tests**

Run: `python -m pytest tests/test_fixtures.py -v`
Expected: PASS (1 test)

- [ ] **Step 9: Commit**

```bash
git add requirements.txt packages.txt .streamlit hydranl tests
git commit -m "chore: projectopzet, dependencies en testfixtures"
```

---

### Task 2: ffq.txt-parser

**Files:**
- Create: `hydranl/parse_ffq.py`
- Test: `tests/test_parse_ffq.py`

**Interfaces:**
- Produces: `parse_ffq(path: Path) -> pandas.DataFrame` met kolommen `waterstand` (float), `frequentie` (float); aantal rijen == getal op regel 1.

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path
from hydranl.parse_ffq import parse_ffq


def test_parse_ffq_shape1(calc_dirs):
    df = parse_ffq(calc_dirs["1_Shape_1"] / "ffq.txt")
    assert list(df.columns) == ["waterstand", "frequentie"]
    assert len(df) == 76
    assert df.iloc[0]["waterstand"] == 2.5
    assert abs(df.iloc[0]["frequentie"] - 0.1975854) < 1e-9
    assert df.iloc[-1]["waterstand"] == 4.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_parse_ffq.py -v`
Expected: FAIL (ModuleNotFoundError: hydranl.parse_ffq)

- [ ] **Step 3: Write minimal implementation**

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_parse_ffq.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add hydranl/parse_ffq.py tests/test_parse_ffq.py
git commit -m "feat: ffq.txt-parser"
```

---

### Task 3: invoer.hyd-parser

**Files:**
- Create: `hydranl/parse_invoer.py`
- Test: `tests/test_parse_invoer.py`

**Interfaces:**
- Produces: `parse_invoer(path: Path) -> dict[str, str | list[str]]`. Elke `KEY = value`-regel wordt een sleutel; omringende quotes en spaties worden gestript. Sleutels die meermaals voorkomen (bv. `FREQ`) worden een lijst van strings. Regels die met `;` beginnen of geen `=` bevatten worden overgeslagen.

- [ ] **Step 1: Write the failing test**

```python
from hydranl.parse_invoer import parse_invoer


def test_parse_invoer_basics(calc_dirs):
    d = parse_invoer(calc_dirs["1_Shape_1"] / "invoer.hyd")
    assert d["LOCATIE"] == "15-03_00148_1_HY_km0013.70"
    assert d["KLIMAATSCENARIO"] == "3"
    assert d["QCR"] == "0.001"
    assert d["VERSIE"] == "2.8.2"          # quotes gestript
    assert isinstance(d["FREQ"], list)
    assert len(d["FREQ"]) == 8


def test_parse_invoer_variant_differs(calc_dirs):
    a = parse_invoer(calc_dirs["1_Shape_1"] / "invoer.hyd")
    b = parse_invoer(calc_dirs["1_Shape_10"] / "invoer.hyd")
    assert a["KLIMAATSCENARIO"] == "3"
    assert b["KLIMAATSCENARIO"] == "4"
    assert a["ZWS_STIJGING"] == "0.05"
    assert b["ZWS_STIJGING"] == "0.25"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_parse_invoer.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**

```python
from pathlib import Path


def parse_invoer(path: Path) -> dict[str, str | list[str]]:
    """Parse invoer.hyd (KEY = value). Herhaalde sleutels worden een lijst."""
    result: dict[str, str | list[str]] = {}
    for raw in Path(path).read_text(encoding="latin-1").split("\n"):
        line = raw.strip()
        if not line or line.startswith(";") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip()
        if key in result:
            existing = result[key]
            if isinstance(existing, list):
                existing.append(value)
            else:
                result[key] = [existing, value]
        else:
            result[key] = value
    return result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_parse_invoer.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add hydranl/parse_invoer.py tests/test_parse_invoer.py
git commit -m "feat: invoer.hyd-parser"
```

---

### Task 4: uitvoer.html-parser — metadata en HBN-tabellen

**Files:**
- Create: `hydranl/parse_uitvoer.py`
- Test: `tests/test_parse_uitvoer.py`

**Interfaces:**
- Produces:
  - `html_to_text(path: Path) -> str` — strip `<...>`-tags, open als latin-1.
  - `parse_metadata(text: str) -> dict[str, str]` — sleutels `locatie`, `x`, `y`, `versie`, `datum`, `kritiek_overslagdebiet`.
  - `parse_hbn_frequentie(text: str) -> pandas.DataFrame` — kolommen `frequentie` (1/jaar, int), `hbn` (float).
  - `parse_hbn_terugkeertijd(text: str) -> pandas.DataFrame` — kolommen `terugkeertijd` (int), `hbn` (float).

- [ ] **Step 1: Write the failing test**

```python
from hydranl.parse_uitvoer import (
    html_to_text, parse_metadata, parse_hbn_frequentie, parse_hbn_terugkeertijd,
)


def test_metadata(calc_dirs):
    text = html_to_text(calc_dirs["1_Shape_1"] / "uitvoer.html")
    meta = parse_metadata(text)
    assert meta["locatie"] == "15-03_00148_1_HY_km0013.70"
    assert meta["x"] == "102499"
    assert meta["y"] == "438900"
    assert meta["versie"] == "2.8.2"


def test_hbn_frequentie(calc_dirs):
    text = html_to_text(calc_dirs["1_Shape_1"] / "uitvoer.html")
    df = parse_hbn_frequentie(text)
    assert list(df.columns) == ["frequentie", "hbn"]
    row = df[df["frequentie"] == 3000].iloc[0]
    assert abs(row["hbn"] - 3.295) < 1e-6
    row2 = df[df["frequentie"] == 833333].iloc[0]
    assert abs(row2["hbn"] - 3.918) < 1e-6


def test_hbn_terugkeertijd(calc_dirs):
    text = html_to_text(calc_dirs["1_Shape_1"] / "uitvoer.html")
    df = parse_hbn_terugkeertijd(text)
    assert abs(df[df["terugkeertijd"] == 10].iloc[0]["hbn"] - 2.582) < 1e-6
    assert abs(df[df["terugkeertijd"] == 100000].iloc[0]["hbn"] - 3.676) < 1e-6
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_parse_uitvoer.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_parse_uitvoer.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add hydranl/parse_uitvoer.py tests/test_parse_uitvoer.py
git commit -m "feat: uitvoer.html-parser voor metadata en HBN-tabellen"
```

---

### Task 5: uitvoer.html-parser — illustratiepunten

**Files:**
- Modify: `hydranl/parse_uitvoer.py`
- Test: `tests/test_parse_illustratiepunten.py`

**Interfaces:**
- Consumes: `html_to_text` uit Task 4.
- Produces: `parse_illustratiepunten(text: str) -> list[dict]`. Elk dict: `{"hbn": float, "terugkeertijd": int, "tabellen": list[dict]}`, waarbij elke tabel `{"toestand": str, "rijen": pandas.DataFrame}` is met kolommen `windrichting, zeews, q_rijn, q_maas, windsn, h_teen, hm0, tm, golfr, ov_freq`. Waarde `--` wordt `None`.

- [ ] **Step 1: Write the failing test**

```python
from hydranl.parse_uitvoer import html_to_text, parse_illustratiepunten


def test_illustratiepunten(calc_dirs):
    text = html_to_text(calc_dirs["1_Shape_1"] / "uitvoer.html")
    blokken = parse_illustratiepunten(text)
    assert len(blokken) >= 1
    eerste = blokken[0]
    assert abs(eerste["hbn"] - 3.29) < 1e-6
    assert eerste["terugkeertijd"] == 3000
    assert len(eerste["tabellen"]) >= 1
    df = eerste["tabellen"][0]["rijen"]
    nno = df[df["windrichting"] == "NNO"].iloc[0]
    assert abs(nno["zeews"] - 1.35) < 1e-6
    assert nno["q_rijn"] == 10000
    assert nno["q_maas"] is None      # '--' -> None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_parse_illustratiepunten.py -v`
Expected: FAIL (ImportError: parse_illustratiepunten)

- [ ] **Step 3: Write minimal implementation** (voeg toe aan `hydranl/parse_uitvoer.py`)

```python
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
        # Sub-tabellen beginnen bij een toestand-regel en bevatten '|'-rijen.
        for tm in re.finditer(
            r"(Geopende|Gesloten)[^\n]*\n((?:.*\|.*\n)+)", blok
        ):
            toestand = tm.group(1) + tm.group(0).split("\n")[0][8:]
            rijen = []
            for regel in tm.group(2).split("\n"):
                if "|" not in regel or "---" in regel:
                    continue
                cellen = [c.strip() for c in regel.split("|")]
                if not re.match(r"[A-Z]", cellen[0]):
                    continue
                waarden = [cellen[0]] + [_cel(c) for c in cellen[1:]]
                rijen.append(waarden[: len(_KOLOMMEN)])
            if rijen:
                df = pd.DataFrame(rijen, columns=_KOLOMMEN[: len(rijen[0])])
                tabellen.append({"toestand": toestand.strip(), "rijen": df})
        blokken.append({
            "hbn": float(m.group(1)),
            "terugkeertijd": int(m.group(2)),
            "tabellen": tabellen,
        })
    return blokken
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_parse_illustratiepunten.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add hydranl/parse_uitvoer.py tests/test_parse_illustratiepunten.py
git commit -m "feat: illustratiepunten-parser"
```

---

### Task 6: Datamodel en archief/ontdekking

**Files:**
- Create: `hydranl/model.py`
- Create: `hydranl/archive.py`
- Test: `tests/test_model.py`, `tests/test_archive.py`

**Interfaces:**
- Consumes: `parse_invoer`, `parse_ffq`, `html_to_text`, `parse_metadata`, `parse_hbn_frequentie`, `parse_hbn_terugkeertijd`, `parse_illustratiepunten`.
- Produces:
  - `Berekening` dataclass met velden `naam: str`, `invoer: dict`, `metadata: dict`, `hbn_frequentie: DataFrame`, `hbn_terugkeertijd: DataFrame`, `illustratiepunten: list[dict]`, `ffq: DataFrame`.
  - `laad_berekening(map: Path) -> Berekening`.
  - `ontdek_berekeningen(root: Path) -> list[Path]` — alle mappen met `invoer.hyd`.
  - `uitpakken(archief: Path, doel: Path) -> Path` — pakt `.zip` (zipfile) of `.rar` (rarfile) uit naar `doel`; geeft `doel` terug.

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path
import zipfile
from hydranl.model import laad_berekening, Berekening
from hydranl.archive import ontdek_berekeningen, uitpakken


def test_laad_berekening(calc_dirs):
    b = laad_berekening(calc_dirs["1_Shape_1"])
    assert isinstance(b, Berekening)
    assert b.naam == "1_Shape_1"
    assert b.invoer["KLIMAATSCENARIO"] == "3"
    assert abs(b.hbn_frequentie[b.hbn_frequentie.frequentie == 3000].iloc[0].hbn - 3.295) < 1e-6
    assert len(b.ffq) == 76


def test_ontdek_berekeningen(sample_dir):
    paden = ontdek_berekeningen(sample_dir)
    namen = {p.name for p in paden}
    assert namen == {"1_Shape_1", "1_Shape_10", "Def v01_Shape_1"}


def test_uitpakken_zip(tmp_path, calc_dirs):
    zippad = tmp_path / "test.zip"
    with zipfile.ZipFile(zippad, "w") as z:
        for f in ("invoer.hyd", "uitvoer.html", "ffq.txt"):
            z.write(calc_dirs["1_Shape_1"] / f, f"Ber/1_Shape_1/{f}")
    doel = uitpakken(zippad, tmp_path / "out")
    assert ontdek_berekeningen(doel)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_model.py tests/test_archive.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**

`hydranl/model.py`:

```python
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
```

`hydranl/archive.py`:

```python
import zipfile
from pathlib import Path


def ontdek_berekeningen(root: Path) -> list[Path]:
    root = Path(root)
    return sorted({p.parent for p in root.rglob("invoer.hyd")}, key=lambda p: p.name)


def uitpakken(archief: Path, doel: Path) -> Path:
    archief, doel = Path(archief), Path(doel)
    doel.mkdir(parents=True, exist_ok=True)
    suffix = archief.suffix.lower()
    if suffix == ".zip":
        with zipfile.ZipFile(archief) as z:
            z.extractall(doel)
    elif suffix == ".rar":
        import rarfile
        with rarfile.RarFile(archief) as r:
            r.extractall(doel)
    else:
        raise ValueError(f"Niet-ondersteund archief: {suffix}. Gebruik .zip of .rar.")
    return doel
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_model.py tests/test_archive.py -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add hydranl/model.py hydranl/archive.py tests/test_model.py tests/test_archive.py
git commit -m "feat: datamodel, berekening laden en archief uitpakken"
```

---

### Task 7: Kennisbank

**Files:**
- Create: `data/parameters.yaml`
- Create: `hydranl/knowledge.py`
- Test: `tests/test_knowledge.py`

**Interfaces:**
- Produces:
  - `laad_kennisbank() -> dict[str, dict]` — leest `data/parameters.yaml`.
  - `beschrijf(key: str, kennis: dict) -> dict` — geeft `{"label", "uitleg", "eenheid", "impact"}`; onbekende sleutel geeft `label=key`, lege uitleg, `impact="onbekend"`.
  - `duid_waarde(key: str, waarde: str, kennis: dict) -> str` — vertaalt codewaarden (bv. KLIMAATSCENARIO 3→"G (gematigd)") of geeft de waarde terug.

- [ ] **Step 1: data/parameters.yaml** (kernparameters; uitbreidbaar)

```yaml
KLIMAATSCENARIO:
  label: "Klimaatscenario"
  eenheid: ""
  uitleg: "Aangenomen klimaatverandering. Bepaalt zeespiegelstijging en afvoerstatistiek. W (warm) is zwaarder dan G (gematigd)."
  impact: "hoger"
  waarden:
    "3": "G (gematigd)"
    "4": "W (warm)"
ZWS_STIJGING:
  label: "Zeewaterstandstijging"
  eenheid: "m"
  uitleg: "Aangenomen stijging van de zeewaterstand. Een hogere waarde verhoogt de belasting op de kering."
  impact: "hoger"
QAFTOP:
  label: "Aftopdebiet"
  eenheid: "m³/s"
  uitleg: "Rivierafvoer waarboven wordt afgetopt in de statistiek. Beïnvloedt de zwaarste meegenomen afvoeren."
  impact: "context"
QCR:
  label: "Kritiek overslagdebiet"
  eenheid: "l/s/m"
  uitleg: "Toelaatbare golfoverslag over de kering. Een hogere toelaatbare waarde geeft een lager benodigd belastingniveau."
  impact: "lager"
OVKANSQ:
  label: "Afvoerstatistiek (overschrijdingskansen)"
  eenheid: ""
  uitleg: "Bestand met overschrijdingskansen van de rivierafvoer. De keuze G/W bepaalt de zwaarte van de statistiek."
  impact: "context"
FACTOR_TP_TM:
  label: "Factor Tp/Tm-1,0"
  eenheid: "-"
  uitleg: "Omrekenfactor tussen piek- en spectrale golfperiode. Beïnvloedt de berekende golfoverslag."
  impact: "context"
MU:
  label: "Mu (keringonzekerheid)"
  eenheid: "-"
  uitleg: "Verwachtingswaarde van de onzekerheid in het keringgedrag."
  impact: "context"
SIGMA:
  label: "Sigma (keringonzekerheid)"
  eenheid: "-"
  uitleg: "Spreiding van de onzekerheid in het keringgedrag. Meer spreiding kan de belasting verhogen."
  impact: "context"
```

- [ ] **Step 2: Write the failing test**

```python
from hydranl.knowledge import laad_kennisbank, beschrijf, duid_waarde


def test_laad_en_beschrijf():
    k = laad_kennisbank()
    b = beschrijf("KLIMAATSCENARIO", k)
    assert b["label"] == "Klimaatscenario"
    assert b["impact"] == "hoger"
    assert "klimaat" in b["uitleg"].lower()


def test_onbekende_parameter():
    k = laad_kennisbank()
    b = beschrijf("ONBEKEND_XYZ", k)
    assert b["label"] == "ONBEKEND_XYZ"
    assert b["impact"] == "onbekend"


def test_duid_waarde():
    k = laad_kennisbank()
    assert duid_waarde("KLIMAATSCENARIO", "4", k) == "W (warm)"
    assert duid_waarde("ZWS_STIJGING", "0.25", k) == "0.25"
```

- [ ] **Step 3: Run test to verify it fails**

Run: `python -m pytest tests/test_knowledge.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 4: Write minimal implementation**

```python
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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_knowledge.py -v`
Expected: PASS (3 tests)

- [ ] **Step 6: Commit**

```bash
git add data/parameters.yaml hydranl/knowledge.py tests/test_knowledge.py
git commit -m "feat: kennisbank met parameteruitleg"
```

---

### Task 8: Vergelijking (invoer-diff + HBN-uitlijning)

**Files:**
- Create: `hydranl/compare.py`
- Test: `tests/test_compare.py`

**Interfaces:**
- Consumes: `Berekening` (Task 6).
- Produces:
  - `vergelijk_invoer(berekeningen: list[Berekening], negeer: set[str] | None = None) -> pandas.DataFrame` — index = parameter, kolom per berekeningnaam met de waarde; alleen rijen waar niet alle waarden gelijk zijn wanneer `alleen_verschillen=True`. Signatuur: `vergelijk_invoer(berekeningen, alleen_verschillen=False, negeer=None)`.
  - `hbn_matrix(berekeningen: list[Berekening]) -> pandas.DataFrame` — index = frequentie (1/jaar), kolom per berekeningnaam met HBN.
  - `hbn_delta(matrix: DataFrame, referentie: str) -> DataFrame` — zelfde vorm, waarden = (kolom − referentie) in **cm**, afgerond op 1 decimaal.

- [ ] **Step 1: Write the failing test**

```python
from hydranl.model import laad_berekening
from hydranl.compare import vergelijk_invoer, hbn_matrix, hbn_delta


def _berekeningen(calc_dirs):
    return [laad_berekening(calc_dirs[n]) for n in ("1_Shape_1", "1_Shape_10")]


def test_vergelijk_invoer_verschillen(calc_dirs):
    df = vergelijk_invoer(_berekeningen(calc_dirs), alleen_verschillen=True,
                          negeer={"DATBER", "UITVOERBESTAND"})
    assert "KLIMAATSCENARIO" in df.index
    assert "QCR" in df.index
    assert "LOCATIE" not in df.index          # gelijk => weggefilterd
    assert df.loc["KLIMAATSCENARIO", "1_Shape_1"] == "3"
    assert df.loc["KLIMAATSCENARIO", "1_Shape_10"] == "4"


def test_hbn_matrix_en_delta(calc_dirs):
    bers = _berekeningen(calc_dirs)
    m = hbn_matrix(bers)
    assert abs(m.loc[3000, "1_Shape_1"] - 3.295) < 1e-6
    d = hbn_delta(m, referentie="1_Shape_1")
    assert d.loc[3000, "1_Shape_1"] == 0.0
    # variant wijkt af t.o.v. referentie (in cm)
    assert d.loc[3000, "1_Shape_10"] != 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_compare.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**

```python
import pandas as pd


def vergelijk_invoer(berekeningen, alleen_verschillen=False, negeer=None) -> pd.DataFrame:
    negeer = negeer or set()
    kolommen = {}
    for b in berekeningen:
        kolommen[b.naam] = {
            k: (", ".join(v) if isinstance(v, list) else v)
            for k, v in b.invoer.items() if k not in negeer
        }
    df = pd.DataFrame(kolommen)
    df = df.sort_index()
    if alleen_verschillen:
        verschilt = df.apply(lambda r: r.nunique(dropna=False) > 1, axis=1)
        df = df[verschilt]
    return df


def hbn_matrix(berekeningen) -> pd.DataFrame:
    series = {b.naam: b.hbn_frequentie.set_index("frequentie")["hbn"] for b in berekeningen}
    return pd.DataFrame(series).sort_index()


def hbn_delta(matrix: pd.DataFrame, referentie: str) -> pd.DataFrame:
    ref = matrix[referentie]
    return ((matrix.sub(ref, axis=0)) * 100).round(1)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_compare.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add hydranl/compare.py tests/test_compare.py
git commit -m "feat: invoer-diff en HBN-vergelijking met delta"
```

---

### Task 9: Impact-duiding (regelgebaseerd)

**Files:**
- Create: `hydranl/narrative.py`
- Test: `tests/test_narrative.py`

**Interfaces:**
- Consumes: `Berekening`, `vergelijk_invoer`, `hbn_matrix`, `hbn_delta`, `laad_kennisbank`, `beschrijf`, `duid_waarde`.
- Produces: `duiding(referentie: Berekening, variant: Berekening, kennis: dict, kernfrequentie: int = 3000, negeer: set[str] | None = None) -> str` — een Nederlandstalige alinea die (a) de gewijzigde parameters met uitleg en (b) de Δ HBN in cm op `kernfrequentie` benoemt. Bij geen verschillen: zin dat de invoer identiek is.

- [ ] **Step 1: Write the failing test**

```python
from hydranl.model import laad_berekening
from hydranl.knowledge import laad_kennisbank
from hydranl.narrative import duiding


def test_duiding_noemt_parameters_en_delta(calc_dirs):
    ref = laad_berekening(calc_dirs["1_Shape_1"])
    var = laad_berekening(calc_dirs["1_Shape_10"])
    tekst = duiding(ref, var, laad_kennisbank(),
                    negeer={"DATBER", "UITVOERBESTAND"})
    assert "Klimaatscenario" in tekst
    assert "cm" in tekst
    assert var.naam in tekst


def test_duiding_identiek(calc_dirs):
    ref = laad_berekening(calc_dirs["1_Shape_1"])
    tekst = duiding(ref, ref, laad_kennisbank(),
                    negeer={"DATBER", "UITVOERBESTAND"})
    assert "identiek" in tekst.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_narrative.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**

```python
from .compare import vergelijk_invoer, hbn_matrix, hbn_delta
from .knowledge import beschrijf, duid_waarde


def duiding(referentie, variant, kennis, kernfrequentie=3000, negeer=None):
    negeer = negeer or {"DATBER", "UITVOERBESTAND"}
    diff = vergelijk_invoer([referentie, variant], alleen_verschillen=True, negeer=negeer)
    if diff.empty:
        return (f"De invoer van '{variant.naam}' is identiek aan de referentie "
                f"'{referentie.naam}'. Er wordt geen verschil in resultaat verwacht.")

    zinnen = [f"Variant '{variant.naam}' verschilt van referentie "
              f"'{referentie.naam}' op de volgende punten:"]
    for param in diff.index:
        info = beschrijf(param, kennis)
        ref_w = duid_waarde(param, diff.loc[param, referentie.naam], kennis)
        var_w = duid_waarde(param, diff.loc[param, variant.naam], kennis)
        eenheid = f" {info['eenheid']}" if info["eenheid"] else ""
        regel = f"- {info['label']}: {var_w}{eenheid} (referentie: {ref_w}{eenheid})."
        if info["uitleg"]:
            regel += f" {info['uitleg']}"
        zinnen.append(regel)

    matrix = hbn_matrix([referentie, variant])
    if kernfrequentie in matrix.index:
        d = hbn_delta(matrix, referentie.naam).loc[kernfrequentie, variant.naam]
        richting = "hoger" if d > 0 else "lager" if d < 0 else "gelijk"
        zinnen.append(
            f"Effect: bij frequentie 1/{kernfrequentie} is het hydraulisch "
            f"belastingniveau {abs(d):.1f} cm {richting} dan de referentie.")
    return "\n".join(zinnen)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_narrative.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add hydranl/narrative.py tests/test_narrative.py
git commit -m "feat: regelgebaseerde impact-duiding"
```

---

### Task 10: Streamlit-UI

**Files:**
- Create: `app.py`
- Test: handmatig (Streamlit-UI, geen unit-test)

**Interfaces:**
- Consumes: alle `hydranl`-modules.

- [ ] **Step 1: Schrijf app.py**

```python
import tempfile
from pathlib import Path

import streamlit as st

from hydranl.archive import ontdek_berekeningen, uitpakken
from hydranl.model import laad_berekening
from hydranl.compare import vergelijk_invoer, hbn_matrix, hbn_delta
from hydranl.knowledge import laad_kennisbank, beschrijf
from hydranl.narrative import duiding

NEGEER = {"DATBER", "UITVOERBESTAND", "USERNAME", "USER", "MEMO"}
ROOT = Path(__file__).resolve().parent

st.set_page_config(page_title="HydraNL Vergelijkingstool", layout="wide")
st.title("HydraNL Vergelijkingstool")
st.caption("Vergelijk HydraNL-berekeningen en begrijp de verschillen in gewone taal.")


@st.cache_data(show_spinner=False)
def _laad(paden: list[str]):
    return [laad_berekening(Path(p)) for p in paden]


def _verzamel_paden() -> list[Path]:
    paden: list[Path] = []
    keuze = st.radio("Bron", ["Demo-data", "Upload archief (.zip/.rar)"], horizontal=True)
    if keuze == "Demo-data":
        paden = ontdek_berekeningen(ROOT / "sample_data")
    else:
        bestanden = st.file_uploader("Archief(en)", type=["zip", "rar"],
                                     accept_multiple_files=True)
        if bestanden:
            tmp = Path(tempfile.mkdtemp())
            for f in bestanden:
                arch = tmp / f.name
                arch.write_bytes(f.getbuffer())
                try:
                    uitpakken(arch, tmp / f.name.replace(".", "_"))
                except Exception as e:  # noqa: BLE001
                    st.error(f"Kon {f.name} niet uitpakken: {e}. "
                             "Tip: pak je berekeningen in als .zip.")
            paden = ontdek_berekeningen(tmp)
    return paden


paden = _verzamel_paden()
if not paden:
    st.info("Kies demo-data of upload een archief met HydraNL-berekeningen.")
    st.stop()

berekeningen = _laad([str(p) for p in paden])
namen = [b.naam for b in berekeningen]

selectie = st.multiselect("Te vergelijken berekeningen", namen, default=namen)
if not selectie:
    st.stop()
referentie = st.selectbox("Referentie", selectie)
gekozen = [b for b in berekeningen if b.naam in selectie]
kennis = laad_kennisbank()

tab_over, tab_invoer, tab_impact, tab_ill = st.tabs(
    ["Overzicht", "Invoerverschillen", "Impact", "Illustratiepunten"])

with tab_over:
    st.subheader("Hydraulisch belastingniveau (m+NAP) per frequentie")
    matrix = hbn_matrix(gekozen)
    st.line_chart(matrix)
    st.dataframe(matrix.style.format("{:.3f}"))
    st.subheader(f"Verschil t.o.v. referentie '{referentie}' (cm)")
    st.dataframe(hbn_delta(matrix, referentie).style.format("{:+.1f}"))

with tab_invoer:
    st.subheader("Verschillen in invoer")
    diff = vergelijk_invoer(gekozen, alleen_verschillen=True, negeer=NEGEER)
    if diff.empty:
        st.success("Geen verschillen in de invoer gevonden.")
    else:
        uitleg = [beschrijf(p, kennis)["uitleg"] for p in diff.index]
        toon = diff.copy()
        toon.insert(0, "Uitleg", uitleg)
        st.dataframe(toon)

with tab_impact:
    for b in gekozen:
        if b.naam == referentie:
            continue
        st.markdown(f"### {b.naam}")
        ref = next(x for x in gekozen if x.naam == referentie)
        st.write(duiding(ref, b, kennis, negeer=NEGEER))

with tab_ill:
    for b in gekozen:
        with st.expander(f"{b.naam} — illustratiepunten"):
            if not b.illustratiepunten:
                st.write("Geen illustratiepunten gevonden.")
            for blok in b.illustratiepunten:
                st.markdown(f"**HBN {blok['hbn']:.2f} m+NAP — terugkeertijd {blok['terugkeertijd']} jaar**")
                for tabel in blok["tabellen"]:
                    st.caption(tabel["toestand"])
                    st.dataframe(tabel["rijen"])
```

- [ ] **Step 2: Handmatige test**

Run: `python -m streamlit run app.py`
Expected: App opent; met "Demo-data" verschijnen 3 berekeningen; Overzicht toont grafiek + tabellen; Invoerverschillen toont KLIMAATSCENARIO/ZWS_STIJGING/QCR; Impact toont duiding; Illustratiepunten uitklapbaar. Sluit met Ctrl+C.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: Streamlit-UI voor vergelijking en duiding"
```

---

### Task 11: README en projectafronding

**Files:**
- Create: `README.md`
- Test: `python -m pytest` (volledige suite groen)

- [ ] **Step 1: Schrijf README.md**

````markdown
# HydraNL Vergelijkingstool

Vergelijk HydraNL-berekeningen (invoer + uitvoer) en begrijp de verschillen en
hun impact in gewone taal. Gebouwd met Streamlit.

## Wat het doet
- Leest HydraNL-berekeningen (`invoer.hyd`, `uitvoer.html`, `ffq.txt`).
- Toont invoerverschillen met uitleg per parameter.
- Vergelijkt het Hydraulisch Belastingniveau (HBN) per frequentie, incl. Δ in cm.
- Genereert een impact-duiding in gewone taal t.o.v. een gekozen referentie.
- Toont illustratiepunten per windrichting/keringtoestand.

## Lokaal draaien
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```
Voor `.rar`-uploads is het systeempakket `unar` nodig (`sudo apt install unar`).
`.zip` werkt zonder extra software.

## Testen
```bash
python -m pytest
```

## Deploy op Streamlit Community Cloud
1. Push deze repo naar GitHub.
2. Maak op share.streamlit.io een app aan die naar `app.py` wijst.
3. `packages.txt` (met `unar`) en `requirements.txt` worden automatisch gebruikt.

## Kennisbank uitbreiden
Parameteruitleg staat in `data/parameters.yaml`. Voeg parameters toe of pas
teksten aan; onbekende parameters worden getoond zonder uitleg.

## Projectstructuur
- `hydranl/` — parsers, datamodel, vergelijking, kennisbank, duiding (geen Streamlit).
- `app.py` — Streamlit-UI.
- `sample_data/` — 3 voorbeeldberekeningen (ook testfixtures).
- `tests/` — unit-tests.
````

- [ ] **Step 2: Volledige testsuite draaien**

Run: `python -m pytest -v`
Expected: alle tests PASS

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: README met gebruik en deploy-instructies"
```

---

## Self-Review

**Spec coverage:**
- Invoer upload zip/rar + ontdekking → Task 6 (archive) + Task 10 (UI). ✓
- N-vergelijking met referentie → Task 8 + Task 10. ✓
- Invoerverschillen met uitleg → Task 3, 7, 8, 10. ✓
- HBN-resultaten + Δ → Task 4, 8, 10. ✓
- Impact-duiding regelgebaseerd + AI-haak → Task 9 (functie-interface laat AI-variant later toe). ✓
- Illustratiepunten → Task 5 + Task 10. ✓
- Kennisbank YAML → Task 7. ✓
- Foutafhandeling/defensief + fixtures-tests → alle parser-taken + Task 1. ✓
- Deploy (requirements/packages/README) → Task 1 + Task 11. ✓
- Nederlandstalige UI → Task 10. ✓

**Placeholder scan:** geen TBD/TODO; alle code-stappen bevatten volledige code. ✓

**Type consistency:** `Berekening`-veldnamen (`hbn_frequentie`, `hbn_terugkeertijd`, `illustratiepunten`, `invoer`, `metadata`, `ffq`, `naam`) consistent gebruikt in Task 6/8/9/10. `vergelijk_invoer(alleen_verschillen=, negeer=)`, `hbn_matrix`, `hbn_delta(referentie=)` consistent tussen Task 8, 9, 10. `beschrijf`/`duid_waarde`/`laad_kennisbank` consistent tussen Task 7, 9, 10. ✓
