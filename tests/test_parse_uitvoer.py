from hydranl.parse_uitvoer import (
    html_to_text, parse_metadata, parse_hbn_frequentie, parse_hbn_terugkeertijd,
)


def test_metadata(calc_dirs):
    text = html_to_text(calc_dirs["1_Shape_1"] / "uitvoer.html")
    meta = parse_metadata(text)
    assert meta["locatie"] == "15-03_00148_1_HY_km0013.70"
    assert meta["x"] == "102499"
    assert meta["y"] == "438900"
    assert meta["versie"] == "2.8.2"


def test_hbn_frequentie(calc_dirs):
    text = html_to_text(calc_dirs["1_Shape_1"] / "uitvoer.html")
    df = parse_hbn_frequentie(text)
    assert list(df.columns) == ["frequentie", "hbn"]
    row = df[df["frequentie"] == 3000].iloc[0]
    assert abs(row["hbn"] - 3.295) < 1e-6
    row2 = df[df["frequentie"] == 833333].iloc[0]
    assert abs(row2["hbn"] - 3.918) < 1e-6


def test_hbn_terugkeertijd(calc_dirs):
    text = html_to_text(calc_dirs["1_Shape_1"] / "uitvoer.html")
    df = parse_hbn_terugkeertijd(text)
    assert abs(df[df["terugkeertijd"] == 10].iloc[0]["hbn"] - 2.582) < 1e-6
    assert abs(df[df["terugkeertijd"] == 100000].iloc[0]["hbn"] - 3.676) < 1e-6
