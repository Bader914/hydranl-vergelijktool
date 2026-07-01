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
    assert d.loc[3000, "1_Shape_10"] != 0.0
