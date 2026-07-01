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
