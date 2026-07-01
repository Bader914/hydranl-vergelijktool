from hydranl.parse_uitvoer import html_to_text, parse_illustratiepunten


def test_illustratiepunten(calc_dirs):
    text = html_to_text(calc_dirs["1_Shape_1"] / "uitvoer.html")
    blokken = parse_illustratiepunten(text)
    assert len(blokken) >= 1
    eerste = blokken[0]
    assert abs(eerste["hbn"] - 3.29) < 1e-6
    assert eerste["terugkeertijd"] == 3000
    assert len(eerste["tabellen"]) >= 1
    df = eerste["tabellen"][0]["rijen"]
    nno = df[df["windrichting"] == "NNO"].iloc[0]
    assert abs(nno["zeews"] - 1.35) < 1e-6
    assert nno["q_rijn"] == 10000
    assert nno["q_maas"] is None      # '--' -> None
