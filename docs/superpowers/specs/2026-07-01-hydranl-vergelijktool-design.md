# Ontwerp: HydraNL Vergelijkingstool

**Datum:** 2026-07-01
**Status:** Goedgekeurd

## Doel

Een Streamlit-webtool waarmee gebruikers twee of meer HydraNL-berekeningen
naast elkaar kunnen zetten en in **duidelijke, eenvoudige taal** begrijpen:

1. **Wat** er verschilt in de invoer,
2. **Wat** het effect is op de resultaten (Hydraulisch Belastingniveau, HBN),
3. **Waarom/hoe** dat verschil ontstaat (impact-duiding).

Doelgroep: waterschaps-/RWS-medewerkers die HydraNL-uitvoer moeten
interpreteren zonder diep in de rekenkern te duiken.

## Achtergrond: HydraNL

HydraNL is het rekenprogramma van Rijkswaterstaat voor hydraulische
belastingen/randvoorwaarden op primaire waterkeringen (BOI/WBI-kader,
opvolger van Hydra-Zoet/Hydra-Ring). Een berekening bestaat uit een map met:

- `invoer.hyd` — invoerparameters in `KEY = value`-formaat (~60 regels),
  met secties (`;------ algemeen ------` etc.). Bevat o.a. locatie, profiel,
  klimaatscenario, statistiekbestanden, kritiek overslagdebiet, frequenties.
- `uitvoer.html` — het rapport als platte tekst binnen `<pre>`. Bevat:
  - metadata (locatie, X/Y, versie, datum, faalmechanisme, kritiek overslagdebiet);
  - tabel **Frequentie → Hydraulisch Belastingniveau (HBN)** in m+NAP (kernresultaat);
  - tabel **Terugkeertijd → HBN**;
  - **Illustratiepunten**: uitsplitsing per windrichting en keringtoestand.
- `ffq.txt` — frequentielijn: kolommen (waterstand m+NAP, overschrijdingsfrequentie), ~76 punten.
- `uitvoer.log` — voortgangslog (geen analytische waarde; niet geparsed).

Betekenisvolle invoer-knoppen (waargenomen in de demodata):
`KLIMAATSCENARIO` (3=G / 4=W), `ZWS_STIJGING` (zeewaterstandstijging),
`QAFTOP` (aftopdebiet), `QCR` (kritiek overslagdebiet), `OVKANSQ`
(afvoerstatistiek G/W), `FACTOR_TP_TM`, `MU/SIGMA/ALFA` (keringonzekerheid).

## Scope-keuzes (vastgelegd)

- **Invoer:** upload van `.zip`/`.rar` of losse bestanden; berekeningen worden
  automatisch herkend aan de aanwezigheid van `invoer.hyd`. RAR via het
  `unar`-systeempakket; ZIP native in Python. Bij falen van RAR op de cloud
  valt de tool terug op een duidelijke melding ("pak in als .zip").
- **Aantal:** N berekeningen tegelijk, met één aangewezen **referentie**
  waartegen Δ en impact-duiding worden bepaald.
- **Toont:** invoerverschillen, HBN-resultaten, impact-duiding, illustratiepunten.
- **Uitleg-motor:** regelgebaseerde kennisbank nu; nette uitbreidingshaak voor
  optionele AI-duiding later (`narrative.py`).
- **Taal:** volledig Nederlandstalige UI.
- **Hosting:** Streamlit (Community Cloud), broncode op GitHub.

## Architectuur

Streamlit-frontend bovenop een pure-Python bibliotheek `hydranl/` die niets van
Streamlit weet (los testbaar, herbruikbaar).

```
hydra-vergelijk/
  app.py                  # Streamlit UI (Nederlandstalig)
  hydranl/
    __init__.py
    archive.py            # zip/rar uitpakken, berekeningen ontdekken (via invoer.hyd)
    parse_invoer.py       # invoer.hyd  -> geordende parameter-structuur
    parse_uitvoer.py      # uitvoer.html -> metadata, HBN-tabellen, illustratiepunten
    parse_ffq.py          # ffq.txt -> (waterstand, frequentie)-tabel
    model.py              # Berekening-dataclass die alles bundelt
    compare.py            # invoer-diff + HBN-uitlijning t.o.v. referentie
    knowledge.py          # laadt en bevraagt de kennisbank
    narrative.py          # regelgebaseerde impact-zinnen (+ haak voor AI)
  data/parameters.yaml    # kennisbank: per parameter label, uitleg, eenheid, impact-richting
  sample_data/            # 3 demo-berekeningen (ook fixtures voor tests)
  tests/                  # unit-tests per parser + compare
  .streamlit/config.toml
  requirements.txt · packages.txt · README.md · .gitignore
```

## Datamodel

`Berekening` (dataclass) bundelt per berekening:

- `naam: str` — mapnaam (bv. `1_Shape_10`).
- `invoer: dict[str, InvoerWaarde]` — geordende parameters; herhaalde sleutels
  (`FREQ`, gegevensblokken) als lijst.
- `hbn_per_frequentie: DataFrame` — kolommen `frequentie` (1/jaar), `hbn` (m+NAP).
- `hbn_per_terugkeertijd: DataFrame` — kolommen `terugkeertijd` (jaar), `hbn`.
- `illustratiepunten: list[IllustratiePuntTabel]` — per terugkeertijd/keringtoestand,
  rijen per windrichting met kolommen zeews., q Rijn, q Maas, windsn., h/Hm0/Tm-1,0/golfr, ov.freq.
- `ffq: DataFrame` — kolommen `waterstand`, `frequentie`.
- `metadata: dict` — locatie, X/Y, versie, datum, faalmechanisme, kritiek overslagdebiet.

Elke parser is klein en apart getest. Parsers zijn defensief: missende velden,
`--`-waarden en decimale komma/punt leiden niet tot een crash.

## Kennisbank (`data/parameters.yaml`)

Per HydraNL-parameter:

```yaml
KLIMAATSCENARIO:
  label: "Klimaatscenario"
  eenheid: ""
  uitleg: "Bepaalt de aangenomen klimaatverandering. 3 = G (gematigd), 4 = W (warm, meer opwarming/zeespiegelstijging)."
  waarden: {3: "G (gematigd)", 4: "W (warm)"}
  impact: "hoger"   # hogere/zwaardere waarde => hoger HBN
```

Onbekende parameters worden getoond zonder uitleg (geen crash). Kennisbank is
platte YAML zodat inhoudelijke experts hem los kunnen bijwerken.

## Impact-duiding (regelgebaseerd)

`narrative.py` bouwt per variant t.o.v. de referentie een tekst uit:

- (a) de lijst gewijzigde invoerparameters + hun uitleg/impact-richting uit de kennisbank;
- (b) de gemeten Δ HBN t.o.v. de referentie op een kernfrequentie.

Voorbeeld: *"Variant '1_Shape_10' gebruikt klimaatscenario W in plaats van G en
een hogere zeewaterstandstijging (0,25 vs 0,05 m). Bij frequentie 1/3000 is het
hydraulisch belastingniveau ~X cm hoger dan de referentie."* Cijfers komen uit de
data; de duiding uit vaste regels. AI-duiding is een optionele, later
in te pluggen functie achter dezelfde interface.

## UI (tabs)

1. **Laden** — upload archief/losse bestanden of gebruik demo-data; kies
   referentie + varianten.
2. **Overzicht** — HBN per frequentie/terugkeertijd als tabel + lijngrafiek;
   Δ-kolommen (cm) t.o.v. referentie.
3. **Invoerverschillen** — diff-tabel: parameter · uitleg · waarde per berekening ·
   gewijzigd-markering; niet-gewijzigde parameters inklapbaar.
4. **Impact** — gegenereerde duiding per variant.
5. **Illustratiepunten** — uitsplitsing per windrichting/keringtoestand, per
   berekening uitklapbaar.

## Foutafhandeling & tests

- Robuuste parsers (defensief tegen missende velden, `--`, decimale komma/punt).
- Unit-tests draaien tegen de 3 meegeleverde berekeningen als vaste fixtures
  (`sample_data/`), zodat parsing gegarandeerd blijft werken. Minimaal:
  `test_parse_invoer`, `test_parse_uitvoer`, `test_parse_ffq`, `test_compare`.

## Deploy

- `requirements.txt`: streamlit, pandas, altair, rarfile, pyyaml.
- `packages.txt`: `unar` (RAR-ondersteuning op Streamlit Cloud).
- `.streamlit/config.toml`: basis-thema.
- `README.md`: lokaal draaien + deploy-instructies (Streamlit Community Cloud).
- Broncode naar GitHub; het RAR-bronarchief zelf blijft buiten de repo (`.gitignore`).

## Niet in scope (YAGNI)

- Bewerken/herrekenen van HydraNL-berekeningen (alleen lezen/vergelijken).
- Parsen van `uitvoer.log`.
- Gebruikersaccounts/authenticatie.
- AI-duiding in de eerste versie (wel voorbereid).
