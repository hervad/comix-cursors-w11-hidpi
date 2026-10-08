# Port status: Comix Cursors

- gnome-look page: https://www.gnome-look.org/p/999996 (store API 2026-10-08: version 0.10.1, 4 downloads -
  ComixCursors, -LH, -Opaque, -LH-Opaque - each holding 12 themes: 6 colours x Regular/Slim = 48 themes)
- upstream: https://gitlab.com/limitland/comixcursors, submodule `upstream/` pinned to
  `115b7a03dc731865cca214f9881a9afa1249eb09` (tag 0.10.1, 2025-06-15 = latest commit = store version)
- upstream license: GPL-3.0-or-later. `COPYING` (statement: "either version 3 ... or (at your option) any later
  version"; points to `LICENSE.GPL`), `LICENSE.GPL` (GPL v3 text), `AUTHORS` - all copied byte-for-byte under their
  own names (toolkit accepts LICENSE.GPL as a notice file since a93cb4a)
- variants: all 48 on the page (maintainer's choice 2026-10-08): 6 colours x {Regular, Slim} x {translucent, Opaque}
  x {right-, left-handed}

## Status
Builds and validates locally (48 variants); Windows loader 816/816, .ani timing 144/144. Not yet a GitHub repo.
Needs toolkit **v0.3.0** (single-file rotate, mirror_hotspots, LICENSE.GPL); not tagged yet.

## Findings
- **How upstream builds** (`bin/build-cursors`): per-cursor SVG templates in `svg/RightHanded` and `svg/LeftHanded`
  get `sed` substitutions (placeholder colours, outline width, two opacities) from `ComixCursorsConfigs/<Colour>.CONFIG`
  plus `<Include>.INCLUDE`, then `rsvg-convert`. There is no other generation step, so no `pre-build` is needed: the
  substitutions are each variant's `recolor` (plain text replacement, applied in order like chained sed -e).
  `tools/variants_from_configs.py` generates the 48 blocks. Upstream quirk kept: for every colour except Black the
  outline colour #111111 is later replaced by the shadow colour #000000 (sed order), so outlines are black.
- **Equivalence** (2026-10-08): upstream's own `svg_substitutions` (extracted verbatim, run with Git Bash sed; `bc`
  replaced by an awk stand-in) vs the toolkit's recolor: 720 of 720 SVGs (48 variants x 15 cursors) byte-identical.
  Opacity cross-check against the store build (compiled Xcursor, Black, 64 px): our resvg render gives the same
  alpha histogram (shadow 1, body 189/190; Opaque body 255).
- **Canvas:** SVGs are `width="500" height="500"`, viewBox 1000; HOTSPOTS are in 500 units -> `design_canvas = 500`.
  Hotspots checked on renders: tips on tips, centred cursors within a few units of the drawing's centre.
  LeftHanded HOTSPOTS = 500 - x for every Windows role (zoom-in/out differ, not used) -> `mirror_hotspots`.
- **Animations:** one element rotated per frame about its own `rotate(0,cx,cy)` (ids path1441 / path1398 /
  flowRoot1441; LH files have mirrored centres, so the centre is read from the element). busy 36 x 10 deg,
  working 24 x 15 deg, help 2 x 180 deg; store build: 50 ms per frame, help 2000 + 500 ms -> 3 jiffies, [120, 30].
- **Shadow:** faint blur filter (26 filtered elements per variant). v0.1.0 stripped it (ADR-14). v0.1.1 KEEPS it
  (maintainer, 2026-10-08, after seeing rough edges at size 1): the Black family has a LIGHT outline (white, 70 %)
  on a DARK body; on light pages that outline only reads against upstream's shadow. 32 px comparison vs the store
  build: store (rsvg + shadow) ~ resvg + shadow; without shadow the outline disappears on light backgrounds (both
  renderers). Windows' pointer shadow was ON and did not compensate. renderer = resvg (cairosvg draws blur hard,
  ADR-12). Outline/body survey of every shipped arrow (Polar, Material, Future, Comix, Capitaine, Layan, aero): only
  the Comix Black family (and published Capitaine Dark, which has its own grey halo and looks clean) has a light
  outline on a dark body. Halo scan (hidden shapes): clean.
- **Move** = upstream's `all-scroll`, an open hand (Comix has no four-way arrow); hotspot (190,90) = fingertip.
- **Sizes:** v0.1.1 (shadow): largest .ani 966 KB (< 1 MB budget); largest image offset 22,253 of 65,535.
- **Load cost** v0.1.1 (Windows 11 25H2, same run as aero): static 0.18-0.28 ms (aero 0.13-0.16), animated
  2.5-6.5 ms at 32-96 px (aero 1.3-4.1), 32-49 ms at 256 px (aero 20); 0 GDI/USER handles leaked over 300 loads.
- **Preview:** docs/preview.png = 6 colours (Regular, right-handed); docs/styles.png = Blue in Regular / Slim /
  Opaque / left-handed on one background (`preview --background light`).

## Checklist
- [x] Upstream pinned (submodule at tag 0.10.1 = latest)
- [x] License files copied byte-for-byte under their own names
- [x] design_canvas confirmed (500)
- [x] All 17 roles mapped; Pin/Person = link; Move = open hand
- [x] Hotspots from HOTSPOTS, checked on renders; LH mirrored
- [x] 48 variants generated from upstream configs; equivalence with upstream's sed proven
- [x] `w11cursor build` + `validate` green locally (48); Test-LoadCursors 816/816; Get-AniFrameTiming 144/144
- [x] README, CREDITS, previews
- [x] Toolkit v0.3.0 tagged; GitHub repo created (public); CI green (48 built, 816 loaded on Windows)
- [x] Installed (Blue, Opaque Black, LH White) and checked on screen; v0.1.0 released (2026-10-08)
- [ ] v0.1.1: upstream shadow kept (rough edges of the Black family at size 1)
