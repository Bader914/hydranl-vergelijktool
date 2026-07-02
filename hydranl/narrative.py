from .compare import vergelijk_invoer, hbn_matrix, hbn_delta
from .knowledge import beschrijf, duid_waarde


def _num(x):
    return x if isinstance(x, (int, float)) and x == x else 0.0


def dominant_mechanisme(berekening) -> dict | None:
    """Bepaal uit het eerste illustratiepunten-blok welke keringtoestand en
    windrichting de belasting domineren. Geeft None als er geen data is."""
    if not berekening.illustratiepunten:
        return None
    blok = berekening.illustratiepunten[0]
    tabellen = [t for t in blok["tabellen"] if "ov_pct" in t["rijen"].columns]
    if not tabellen:
        return None

    def somp(t):
        return sum(_num(v) for v in t["rijen"]["ov_pct"])

    dom = max(tabellen, key=somp)
    df = dom["rijen"].copy()
    df["_p"] = [_num(v) for v in df["ov_pct"]]
    top = df.sort_values("_p", ascending=False).iloc[0]
    return {
        "hbn": blok["hbn"],
        "terugkeertijd": blok["terugkeertijd"],
        "toestand": dom["toestand"],
        "toestand_aandeel": round(somp(dom), 1),
        "windrichting": top["windrichting"],
        "wind_aandeel": round(float(top["_p"]), 1),
        "zeewaterstand": top.get("zeews"),
        "q_rijn": top.get("q_rijn"),
        "windsnelheid": top.get("windsn"),
    }


def hbn_profiel(referentie, variant) -> dict:
    """Statistiek van het HBN-verschil (variant - referentie) in cm over alle
    gedeelde frequenties."""
    matrix = hbn_matrix([referentie, variant])
    delta = hbn_delta(matrix, referentie.naam)[variant.naam].dropna()
    if delta.empty:
        return {}
    zwaarste = delta.abs().idxmax()
    trend = "groeit" if abs(delta.iloc[-1]) > abs(delta.iloc[0]) + 1 else (
        "krimpt" if abs(delta.iloc[-1]) < abs(delta.iloc[0]) - 1 else "vlak")
    return {
        "min": float(delta.min()),
        "max": float(delta.max()),
        "gemiddeld": round(float(delta.mean()), 1),
        "bij_3000": float(delta.get(3000, delta.iloc[0])),
        "zwaarste_frequentie": int(zwaarste),
        "zwaarste_delta": float(delta.loc[zwaarste]),
        "trend": trend,
    }


def _leesbaar(waarde: str) -> str:
    """Kort lange bestandspaden in tot de bestandsnaam voor leesbaarheid."""
    tekst = str(waarde)
    if ("\\" in tekst or "/" in tekst) and "." in tekst.rsplit("\\", 1)[-1]:
        return tekst.replace("/", "\\").rsplit("\\", 1)[-1]
    return tekst


def duiding(referentie, variant, kennis, kernfrequentie=3000, negeer=None):
    negeer = negeer or {"DATBER", "UITVOERBESTAND"}
    diff = vergelijk_invoer([referentie, variant], alleen_verschillen=True, negeer=negeer)
    if diff.empty:
        return (f"De invoer van '{variant.naam}' is identiek aan de referentie "
                f"'{referentie.naam}'. Er wordt geen verschil in resultaat verwacht.")

    zinnen = [f"Variant '{variant.naam}' verschilt van referentie "
              f"'{referentie.naam}' op de volgende punten:"]
    for param in diff.index:
        info = beschrijf(param, kennis)
        ref_w = _leesbaar(duid_waarde(param, diff.loc[param, referentie.naam], kennis))
        var_w = _leesbaar(duid_waarde(param, diff.loc[param, variant.naam], kennis))
        eenheid = f" {info['eenheid']}" if info["eenheid"] else ""
        regel = f"- {info['label']}: {var_w}{eenheid} (referentie: {ref_w}{eenheid})."
        if info["uitleg"]:
            regel += f" {info['uitleg']}"
        zinnen.append(regel)

    matrix = hbn_matrix([referentie, variant])
    if kernfrequentie in matrix.index:
        d = hbn_delta(matrix, referentie.naam).loc[kernfrequentie, variant.naam]
        richting = "hoger" if d > 0 else "lager" if d < 0 else "gelijk"
        zinnen.append(
            f"Effect: bij frequentie 1/{kernfrequentie} is het hydraulisch "
            f"belastingniveau {abs(d):.1f} cm {richting} dan de referentie.")
    return "\n".join(zinnen)


def _mechanisme_zin(m: dict) -> str:
    kort = m["toestand"].replace("Hollandsche IJsselkering", "HY-kering")
    return (
        f"De belasting bij 1/{m['terugkeertijd']} wordt gedomineerd door de toestand "
        f"'{kort}' ({m['toestand_aandeel']:.0f}% van de faalkans), vooral bij "
        f"windrichting {m['windrichting']} ({m['wind_aandeel']:.0f}%). "
        f"In dat ontwerppunt: zeewaterstand {m['zeewaterstand']} m+NAP, "
        f"Rijnafvoer {m['q_rijn']} m³/s, wind {m['windsnelheid']} m/s. "
        f"Een hoge zeewaterstand met beperkte rivierafvoer duidt op een "
        f"storm-/zeegedreven belasting; een hoge afvoer op een afvoergedreven belasting."
    )


def volledige_analyse(berekeningen, referentie_naam, kennis, negeer=None) -> str:
    """Uitgebreide, data-gedreven analyse in Markdown: kerncijfers, dominant
    belastingmechanisme per berekening en per variant het effect t.o.v. de
    referentie (verschil in invoer + HBN-profiel over alle frequenties)."""
    negeer = negeer or {"DATBER", "UITVOERBESTAND", "USERNAME", "USER", "MEMO"}
    ref = next(b for b in berekeningen if b.naam == referentie_naam)
    delen = []

    # 1. Context
    meta = ref.metadata
    ctx = [f"## Analyse", "", f"**Referentie:** {ref.naam}"]
    if meta.get("locatie"):
        ctx.append(f"**Locatie:** {meta['locatie']} "
                   f"(x={meta.get('x','?')}, y={meta.get('y','?')})")
    if meta.get("kritiek_overslagdebiet"):
        ctx.append(f"**Faalmechanisme:** golfoverslag, kritiek overslagdebiet "
                   f"{meta['kritiek_overslagdebiet']} l/s/m")
    delen.append("\n".join(ctx))

    # 2. Dominant mechanisme van de referentie
    mref = dominant_mechanisme(ref)
    if mref:
        delen.append("### Belastingmechanisme (referentie)\n\n" + _mechanisme_zin(mref))

    # 3. HBN-niveaus
    matrix = hbn_matrix(berekeningen)
    laag, hoog = matrix.min().min(), matrix.max().max()
    delen.append(
        "### Hydraulisch belastingniveau\n\n"
        f"Over alle berekeningen en frequenties ligt het HBN tussen "
        f"{laag:.2f} en {hoog:.2f} m+NAP. Kleinere frequenties (zeldzamere "
        f"gebeurtenissen) horen bij hogere niveaus.")

    # 4. Per variant het effect
    for b in berekeningen:
        if b.naam == referentie_naam:
            continue
        stukken = [f"### Variant: {b.naam}"]
        diff = vergelijk_invoer([ref, b], alleen_verschillen=True, negeer=negeer)
        if diff.empty:
            stukken.append("Invoer identiek aan de referentie; geen verschil verwacht.")
            delen.append("\n\n".join(stukken))
            continue

        stukken.append("**Gewijzigde invoer:**")
        for param in diff.index:
            info = beschrijf(param, kennis)
            rw = _leesbaar(duid_waarde(param, diff.loc[param, ref.naam], kennis))
            vw = _leesbaar(duid_waarde(param, diff.loc[param, b.naam], kennis))
            eh = f" {info['eenheid']}" if info["eenheid"] else ""
            pijl = {"hoger": "↑ verhoogt HBN", "lager": "↓ verlaagt HBN",
                    "context": "→ situatieafhankelijk", "geen": "· geen effect",
                    "onbekend": "· onbekend"}.get(info["impact"], "")
            regel = f"- **{info['label']}**: {rw}{eh} → {vw}{eh} ({pijl})."
            if info["uitleg"]:
                regel += f" {info['uitleg']}"
            stukken.append(regel)

        prof = hbn_profiel(ref, b)
        if prof:
            richting = "hoger" if prof["bij_3000"] > 0 else "lager"
            stukken.append(
                f"**Effect op HBN:** bij 1/3000 {abs(prof['bij_3000']):.1f} cm "
                f"{richting} dan de referentie; over alle frequenties tussen "
                f"{prof['min']:.1f} en {prof['max']:.1f} cm "
                f"(gemiddeld {prof['gemiddeld']:.1f} cm). Het verschil {prof['trend']} "
                f"richting de zeldzamere frequenties; het grootst bij "
                f"1/{prof['zwaarste_frequentie']} ({prof['zwaarste_delta']:.1f} cm).")

        mvar = dominant_mechanisme(b)
        if mvar and mref and (mvar["toestand"] != mref["toestand"]
                              or abs(mvar["toestand_aandeel"] - mref["toestand_aandeel"]) > 3):
            stukken.append("**Mechanisme:** " + _mechanisme_zin(mvar))

        delen.append("\n\n".join(stukken))

    return "\n\n".join(delen)
