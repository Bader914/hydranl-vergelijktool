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
