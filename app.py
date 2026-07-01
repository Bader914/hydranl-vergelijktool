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
    st.dataframe(matrix.round(3))
    st.subheader(f"Verschil t.o.v. referentie '{referentie}' (cm)")
    st.dataframe(hbn_delta(matrix, referentie))

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
    ref = next(x for x in gekozen if x.naam == referentie)
    for b in gekozen:
        if b.naam == referentie:
            continue
        st.markdown(f"### {b.naam}")
        st.write(duiding(ref, b, kennis, negeer=NEGEER))

with tab_ill:
    for b in gekozen:
        with st.expander(f"{b.naam} — illustratiepunten"):
            if not b.illustratiepunten:
                st.write("Geen illustratiepunten gevonden.")
            for blok in b.illustratiepunten:
                st.markdown(
                    f"**HBN {blok['hbn']:.2f} m+NAP — terugkeertijd "
                    f"{blok['terugkeertijd']} jaar**")
                for tabel in blok["tabellen"]:
                    st.caption(tabel["toestand"])
                    st.dataframe(tabel["rijen"])
