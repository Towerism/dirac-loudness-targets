"""Build the quieter packages from the source package.

Each output curve = source curve + bass shelf + treble shelf - presence dip - gb. Because of the - gb, the result
never rises above the source curve: the bass stays at the source level and everything above it is cut.
  gb      bass lift at 50 Hz, relative to the midrange (ISO 226 extra at 50 Hz for this listening level)
  f1, f2  the bass shelf is flat below f1 and fades out by f2 (raised cosine on a log-frequency axis)
  gt      treble lift reached at 12.5 kHz, fading in from 6.3 kHz. About 60% (package 2) and 45% (package 3) of
          the ISO 226 extra at 12.5 kHz, to keep most of StormAudio's rolloff, which guards against listening
          fatigue. A larger lift can make the treble rise above 8 kHz; tools/check.py fails on such a rise.
  gp      extra cut from 1.6 to 5 kHz, fading in from 1 kHz and out by 12.5 kHz (a faster fade-out
          makes the treble rise near 6.4 kHz). ISO 226 says the ear grows
          relatively more sensitive there as the level drops (0.3 dB at -10, 0.6 dB at -20).
If you change these numbers, update the expected values in tools/check.py to match.

Usage: uv run tools/build.py <source_package_dir> <output_root>"""
import sys
from pathlib import Path

import numpy as np

from targetcurve import Curve, read

PACKAGES = {"stormaudio-minus10dB": dict(gb=4.2, f1=55.0, f2=400.0, gt=1.0, gp=0.3),
            "stormaudio-minus20dB": dict(gb=8.3, f1=55.0, f2=400.0, gt=1.5, gp=0.6)}
TREBLE = (6300.0, 12500.0)
PRESENCE = ((1000.0, 1600.0), (5000.0, 12500.0))  # fade in, fade out
PER_OCTAVE = 24  # breakpoints per octave inside each fade; at 6 the straight segments miss the treble fade by 0.14 dB


def fade(f, lo, hi):
    """1 at or below lo, 0 at or above hi, raised cosine on a log-frequency axis in between."""
    x = np.clip(np.log(np.maximum(np.asarray(f, float), 1e-9) / lo) / np.log(hi / lo), 0, 1)  # 0 Hz counts as below lo
    return 0.5 * (1 + np.cos(np.pi * x))


def change(f, p):
    presence = (1 - fade(f, *PRESENCE[0])) * fade(f, *PRESENCE[1])
    return p["gb"] * fade(f, p["f1"], p["f2"]) + p["gt"] * (1 - fade(f, *TREBLE)) - p["gp"] * presence - p["gb"]


def fade_points(lo, hi):
    return np.geomspace(lo, hi, round(np.log2(hi / lo) * PER_OCTAVE) + 1)


src_dir, out_root = Path(sys.argv[1]), Path(sys.argv[2])
for path in sorted(src_dir.glob("*.targetcurve")):
    curve = read(path)
    for name, p in PACKAGES.items():
        rows = {}
        for f, g, row in zip(curve.freqs, curve.gains, curve.rows):
            d = change(f, p)
            rows[f] = row if d == 0 else f"{row.split()[0]} {g + d:.6g}"  # unchanged points stay byte-identical
        new = np.concatenate([fade_points(p["f1"], p["f2"]), fade_points(*TREBLE), *(fade_points(*e) for e in PRESENCE)])
        known = curve.freqs[curve.freqs > 0]
        for f in new[new <= curve.freqs[-1]]:
            if np.all(np.abs(np.log(f / known)) > 0.005):  # skip points that would crowd a source breakpoint
                rows[f] = f"{f:.6g} {(curve.level(f) + change(f, p))[0]:.6g}"
        out = out_root / name
        out.mkdir(parents=True, exist_ok=True)
        Curve(curve.head, [rows[f] for f in sorted(rows)], curve.tail).write(out / path.name)
