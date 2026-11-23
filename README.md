# SFBG Scientific Animations (source-faithful modular edition)

A minimal Python-based scientific illustration toolkit refactored from the provided
`sfbg_animation.py`. **The default portrait SFBG frame uses the same geometry,
particle trajectories, droplet sampling, shading, fluidising-air arrows and nozzle
as the source script.** No labelling functionality or font outlines are included.

This produces **illustrative schematics**, not validated CFD/DEM trajectories or
numerical population-balance results. Event highlights are conceptual only.

## Install

```bash
python -m pip install -r requirements.txt
```

Install **FFmpeg**, ensuring `ffmpeg` is on your PATH. Works with Python 3.10+.

## First use

```bash
python main.py                        # PNG + 20s MP4 + GIF
python main.py --format png          # Quick still image
python main.py --geometry rectangular --format png
python main.py --spray-entry left --nozzle-x 0.5 --nozzle-y 0.30 --format png
python main.py --spray-entry bottom --nozzle-y 0.94 --spray-direction up --format png
python main.py --scene binary_aggregation --width 1920 --height 640 --format all
python main.py --scene binary_breakage --width 1920 --height 640 --format all
python main.py --scene ternary_breakage --width 1920 --height 640 --format all
```

Use `config.yaml` to customise options permanently. Command-line options override
`config.yaml`. `--output some_folder` chooses the destination folder.

### Source modules

| File | Responsibility |
| --- | --- |
| `main.py` | User-facing command-line controller |
| `config.py` + `config.yaml` | Validated options and defaults |
| `geometry.py` | Tapered/rectangular walls and perforated distributor |
| `particle_style.py` | Exact source-grey matte particle sprites and drawing helpers |
| `particles.py` | Seeded 600-frame periodic recirculation trajectories |
| `spray.py` | Droplet paths/wetting, nozzle location, pipe entry, orientation |
| `mechanisms.py` | Optional horizontal, vessel-free binary/ternary conceptual scenes |
| `render.py` | Full-frame composition |
| `export.py` | PNG/MP4/GIF encoding, with looping GIF |
| `tests/` | Regression, geometry, and export smoke tests |

### Default visual dimensions

- Default scene: `full`; geometry: `tapered`
- Native output: **720 × 1280 portrait**, following the supplied GIF
- 30 frames/s × 20 seconds = 600 frames; fixed random seed 417
- Source particle count: 790 (optionally increase to 1185)
- Right-fed, vertically downward, centred nozzle in the upper chamber
- Default droplets and circulation retain the source's apparent scale and style

### Spray design

`spray.entry` controls the **supply-pipe entry**, while `spray.nozzle_x`,
`spray.nozzle_y` and `spray.direction` set the **actual droplet source and direction**.
The nozzle coordinates are fractions inside the vessel. For example a right-entry
pipe can feed a centred downward nozzle. Changing nozzle settings triggers a
simplified, illustrative forward-targeted droplet model; **the original exact
deposition logic is retained only for the default configuration**.

### PNGs and 16:9

A PNG is rendered at `image_time` seconds. Full-vessel scenes use a portrait
composition and are fitted *without distortion* when you request landscape
output, which leaves white side areas. Horizontal close-ups are designed for
landscape slide strips. No text labels are present in any render.

### Validation

```bash
pytest -q
```

All scenes are conceptual. Even when large agglomerates appear to descend or
smaller breakage fragments rise, those are explanatory trajectories, not a
universal physical rule: actual solids velocities depend on gas flow and drag.
