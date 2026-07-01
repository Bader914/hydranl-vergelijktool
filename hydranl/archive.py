import zipfile
from pathlib import Path


def ontdek_berekeningen(root: Path) -> list[Path]:
    root = Path(root)
    return sorted({p.parent for p in root.rglob("invoer.hyd")}, key=lambda p: p.name)


def uitpakken(archief: Path, doel: Path) -> Path:
    archief, doel = Path(archief), Path(doel)
    doel.mkdir(parents=True, exist_ok=True)
    suffix = archief.suffix.lower()
    if suffix == ".zip":
        with zipfile.ZipFile(archief) as z:
            z.extractall(doel)
    elif suffix == ".rar":
        import rarfile
        with rarfile.RarFile(archief) as r:
            r.extractall(doel)
    else:
        raise ValueError(f"Niet-ondersteund archief: {suffix}. Gebruik .zip of .rar.")
    return doel
