from pathlib import Path
from hydranl.model import laad_berekening
from hydranl.knowledge import laad_kennisbank
from hydranl.narrative import (
    dominant_mechanisme, hbn_profiel, volledige_analyse,
)

S = Path(__file__).resolve().parent.parent / "sample_data"


def _b(naam):
    return laad_berekening(S / naam)


def test_dominant_mechanisme():
    m = dominant_mechanisme(_b("1_Shape_1"))
    assert m["terugkeertijd"] == 3000
    # Beide keringen open domineert; NW-achtige wind bovenaan.
    assert "geopende" in m["toestand"].lower()
    assert m["toestand_aandeel"] > 50
    assert m["windrichting"] in {"WNW", "NW", "W", "NNW"}


def test_hbn_profiel_qcr_verlaagt():
    # calc10 heeft 10x hoger kritiek overslagdebiet -> lager HBN dan calc1.
    prof = hbn_profiel(_b("1_Shape_1"), _b("1_Shape_10"))
    assert prof["bij_3000"] < 0
    assert prof["max"] < 0            # over alle frequenties lager


def test_hbn_profiel_klimaat_verhoogt():
    # Def v01 verschilt van calc1 alleen in klimaat/zeespiegel -> hoger HBN.
    prof = hbn_profiel(_b("1_Shape_1"), _b("Def v01_Shape_1"))
    assert prof["bij_3000"] > 0
    assert prof["min"] > 0            # over alle frequenties hoger


def test_volledige_analyse_bevat_kernonderdelen():
    bers = [_b("1_Shape_1"), _b("Def v01_Shape_1"), _b("1_Shape_10")]
    tekst = volledige_analyse(bers, "1_Shape_1", laad_kennisbank())
    assert "Belastingmechanisme" in tekst
    assert "Hydraulisch belastingniveau" in tekst
    assert "1_Shape_10" in tekst
    assert "Klimaatscenario" in tekst
    assert "cm" in tekst
