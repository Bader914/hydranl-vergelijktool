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
