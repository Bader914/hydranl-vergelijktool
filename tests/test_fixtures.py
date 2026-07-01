def test_three_calculations_present(calc_dirs):
    assert set(calc_dirs) == {"1_Shape_1", "1_Shape_10", "Def v01_Shape_1"}
    for d in calc_dirs.values():
        assert (d / "invoer.hyd").exists()
        assert (d / "uitvoer.html").exists()
        assert (d / "ffq.txt").exists()
