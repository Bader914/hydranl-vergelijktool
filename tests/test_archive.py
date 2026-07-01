import zipfile
from hydranl.archive import ontdek_berekeningen, uitpakken


def test_ontdek_berekeningen(sample_dir):
    paden = ontdek_berekeningen(sample_dir)
    namen = {p.name for p in paden}
    assert namen == {"1_Shape_1", "1_Shape_10", "Def v01_Shape_1"}


def test_uitpakken_zip(tmp_path, calc_dirs):
    zippad = tmp_path / "test.zip"
    with zipfile.ZipFile(zippad, "w") as z:
        for f in ("invoer.hyd", "uitvoer.html", "ffq.txt"):
            z.write(calc_dirs["1_Shape_1"] / f, f"Ber/1_Shape_1/{f}")
    doel = uitpakken(zippad, tmp_path / "out")
    assert ontdek_berekeningen(doel)
