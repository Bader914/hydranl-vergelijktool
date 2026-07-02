# HydraNL Vergelijkingstool

Vergelijk HydraNL-berekeningen (invoer + uitvoer) en begrijp de verschillen en
hun impact in gewone taal. Gebouwd met Streamlit.

[![Deploy op Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=Bader914/hydranl-vergelijktool&branch=main&mainModule=app.py)

## Wat het doet
- Leest HydraNL-berekeningen (`invoer.hyd`, `uitvoer.html`, `ffq.txt`).
- Toont invoerverschillen met uitleg per parameter (kennisbank `data/parameters.yaml`).
- Vergelijkt het Hydraulisch Belastingniveau (HBN) per frequentie, incl. Δ in cm.
- **Genereert een automatische diepe analyse:** dominant belastingmechanisme
  (keringtoestand + windrichting uit de illustratiepunten), HBN-profiel over alle
  frequenties, en per variant het effect met impact-richting per parameter.
- Geeft een beknopte impact-duiding in gewone taal t.o.v. een gekozen referentie.
- Toont illustratiepunten per windrichting/keringtoestand.

Zie [`ANALYSE.md`](ANALYSE.md) voor een uitgewerkte, data-onderbouwde analyse van
de drie voorbeeldberekeningen (incl. decompositie klimaat- vs. ontwerpeffecten).

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
pip install -r requirements-dev.txt
python -m pytest
```

## Deploy op Streamlit Community Cloud
Klik op de **Deploy op Streamlit**-knop bovenaan, of handmatig:
1. Ga naar [share.streamlit.io](https://share.streamlit.io) en log in met GitHub.
2. **New app → From existing repo**.
3. Repository: `Bader914/hydranl-vergelijktool`, branch: `main`, main file: `app.py`.
4. Klik **Deploy**. `requirements.txt` (runtime) en `packages.txt` (`unar`, voor
   `.rar`-uploads) worden automatisch gebruikt.

Python-versie hoeft niet ingesteld te worden; de standaard van Streamlit Cloud
(3.11+) werkt. `.zip`-uploads werken altijd; voor `.rar` zorgt `packages.txt` op
de cloud voor het benodigde `unar`-programma.

## Kennisbank uitbreiden
Parameteruitleg staat in `data/parameters.yaml`. Voeg parameters toe of pas
teksten aan; onbekende parameters worden getoond zonder uitleg.

## Projectstructuur
- `hydranl/` — parsers, datamodel, vergelijking, kennisbank, duiding (geen Streamlit).
- `app.py` — Streamlit-UI.
- `sample_data/` — 3 voorbeeldberekeningen (ook testfixtures).
- `tests/` — unit-tests.
