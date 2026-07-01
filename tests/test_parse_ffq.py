from hydranl.parse_ffq import parse_ffq


def test_parse_ffq_shape1(calc_dirs):
    df = parse_ffq(calc_dirs["1_Shape_1"] / "ffq.txt")
    assert list(df.columns) == ["waterstand", "frequentie"]
    assert len(df) == 76
    assert df.iloc[0]["waterstand"] == 2.5
    assert abs(df.iloc[0]["frequentie"] - 0.1975854) < 1e-9
    assert df.iloc[-1]["waterstand"] == 4.0
