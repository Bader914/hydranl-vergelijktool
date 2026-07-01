from hydranl.model import laad_berekening, Berekening


def test_laad_berekening(calc_dirs):
    b = laad_berekening(calc_dirs["1_Shape_1"])
    assert isinstance(b, Berekening)
    assert b.naam == "1_Shape_1"
    assert b.invoer["KLIMAATSCENARIO"] == "3"
    assert abs(b.hbn_frequentie[b.hbn_frequentie.frequentie == 3000].iloc[0].hbn - 3.295) < 1e-6
    assert len(b.ffq) == 76
