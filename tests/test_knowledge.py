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
