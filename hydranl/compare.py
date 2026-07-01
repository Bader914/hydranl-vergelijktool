import pandas as pd


def vergelijk_invoer(berekeningen, alleen_verschillen=False, negeer=None) -> pd.DataFrame:
    negeer = negeer or set()
    kolommen = {}
    for b in berekeningen:
        kolommen[b.naam] = {
            k: (", ".join(v) if isinstance(v, list) else v)
            for k, v in b.invoer.items() if k not in negeer
        }
    df = pd.DataFrame(kolommen)
    df = df.sort_index()
    if alleen_verschillen:
        verschilt = df.apply(lambda r: r.nunique(dropna=False) > 1, axis=1)
        df = df[verschilt]
    return df


def hbn_matrix(berekeningen) -> pd.DataFrame:
    series = {b.naam: b.hbn_frequentie.set_index("frequentie")["hbn"] for b in berekeningen}
    return pd.DataFrame(series).sort_index()


def hbn_delta(matrix: pd.DataFrame, referentie: str) -> pd.DataFrame:
    ref = matrix[referentie]
    return ((matrix.sub(ref, axis=0)) * 100).round(1)
