from .compare import vergelijk_invoer, hbn_matrix, hbn_delta
from .knowledge import beschrijf, duid_waarde


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
