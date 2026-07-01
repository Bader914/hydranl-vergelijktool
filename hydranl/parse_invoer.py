from pathlib import Path


def parse_invoer(path: Path) -> dict[str, str | list[str]]:
    """Parse invoer.hyd (KEY = value). Herhaalde sleutels worden een lijst."""
    result: dict[str, str | list[str]] = {}
    for raw in Path(path).read_text(encoding="latin-1").split("\n"):
        line = raw.strip()
        if not line or line.startswith(";") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip()
        if key in result:
            existing = result[key]
            if isinstance(existing, list):
                existing.append(value)
            else:
                result[key] = [existing, value]
        else:
            result[key] = value
    return result
