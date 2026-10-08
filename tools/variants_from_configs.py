"""Generate theme.toml's [[variants]] blocks from upstream's ComixCursorsConfigs (run from the repo root).

    python tools/variants_from_configs.py > tools/variants.toml   # then paste between the BEGIN/END GENERATED
                                                                 # VARIANTS markers in theme.toml (git-ignored)

Mirrors upstream bin/build-cursors exactly:
  * <Colour>.CONFIG, then <Include>.INCLUDE (Slim / Opaque / Opaque-Slim) override OUTLINE / CURSORTRANS;
  * SHADOWOPAQ = 1 - SHADOWTRANS and CURSOROPAQ = 1 - CURSORTRANS, formatted like `bc | sed` (".1" -> "0.1",
    "1.0" -> "1");
  * the svg_substitutions sed list, IN ORDER (each replacement sees the result of the previous ones - e.g. a
    #111111 outline is later turned into the #000000 shadow colour, as upstream does);
  * LeftHanded = svg/LeftHanded + mirror_hotspots (its HOTSPOTS are 500 - x for every Windows role).
"""
import re
from decimal import Decimal
from pathlib import Path

CONFIGS = Path("upstream/ComixCursorsConfigs")
COLOURS = ["Black", "Blue", "Green", "Orange", "Red", "White"]
INCLUDES = [None, "Slim", "Opaque", "Opaque-Slim"]        # upstream archive order: plain, Slim, Opaque, Opaque-Slim


def read_shell_vars(path: Path) -> dict[str, str]:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^\s*([A-Z_]+)=(?:"([^"]*)"|([^#\s"]*))\s*(#.*)?$', line)    # quoted values may hold '#'
        if m:
            out[m.group(1)] = m.group(2) if m.group(2) is not None else m.group(3)
    return out


def bc_one_minus(x: str) -> str:
    """`echo "1 - x" | bc | sed 's/^\\./0\\./' | sed 's/\\.0$//'`"""
    v = Decimal(1) - Decimal(x)
    s = format(v, "f")
    if s.startswith("0."):
        s = s[1:]                    # bc prints ".7"
    s = re.sub(r"^\.", "0.", s)
    return re.sub(r"\.0$", "", s)


def substitutions(cfg: dict[str, str]) -> list[tuple[str, str]]:
    return [
        ("#000000", cfg["OUTLINECOLOR"]),
        ("stroke-width:20", f"stroke-width:{cfg['OUTLINE']}"),
        ("#999999", cfg["CURSORCOLORHI"]),
        ("#555555", cfg["CURSORCOLORLO"]),
        ("#999933", cfg["HILIGHTHI"]),
        ("#666600", cfg["HILIGHTLO"]),
        ("#010101", cfg["HAIR"]),
        ("#111111", cfg["SHADOWCOLOR"]),
        ("opacity:0.05", f"opacity:{bc_one_minus(cfg['SHADOWTRANS'])}"),
        ("opacity:0.75", f"opacity:{bc_one_minus(cfg['CURSORTRANS'])}"),
    ]


def main() -> None:
    blocks = []
    for lh in (False, True):
        for inc in INCLUDES:
            for colour in COLOURS:
                cfg = read_shell_vars(CONFIGS / f"{colour}.CONFIG")
                if inc:
                    cfg.update(read_shell_vars(CONFIGS / f"{inc}.INCLUDE"))
                parts = (["LH"] if lh else []) + (inc.split("-") if inc else []) + [colour]
                vid = "-".join(parts).lower()
                name = "Comix " + " ".join(parts) + " W11 HiDPI"
                recolor = ", ".join(f'"{a}" = "{b}"' for a, b in substitutions(cfg))
                block = (f'[[variants]]\nid          = "{vid}"\nscheme_name = "{name}"\n'
                         f'svg_dir     = "upstream/svg/{"LeftHanded" if lh else "RightHanded"}"\n')
                if lh:
                    block += "mirror_hotspots = true\n"
                block += f"recolor     = {{ {recolor} }}\n"
                blocks.append(block)
    print("\n".join(blocks), end="")


if __name__ == "__main__":
    main()
