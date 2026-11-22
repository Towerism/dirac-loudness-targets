"""Plot the three packages for one speaker group, and the change each quieter package makes.
Usage: uv run tools/plot.py <targets_dir> <output.png> [speaker file name]"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from targetcurve import read

targets, out = Path(sys.argv[1]), Path(sys.argv[2])
speaker = sys.argv[3] if len(sys.argv) > 3 else "LCR Cinema Target StormAudio.targetcurve"
packages = {"stormaudio-based": "#6da7ec", "stormaudio-minus10dB": "#2a78d6", "stormaudio-minus20dB": "#104281"}
f = np.geomspace(10, 20000, 600)
base = read(targets / "stormaudio-based" / speaker).level(f)

fig, (top, bottom) = plt.subplots(2, 1, figsize=(10, 7), sharex=True, height_ratios=[2, 1])
for name, color in packages.items():
    level = read(targets / name / speaker).level(f)
    top.plot(f, level, color=color, lw=2, label=name)
    if name != "stormaudio-based":
        bottom.plot(f, level - base, color=color, lw=2, label=name)
top.set_title(speaker.removesuffix(".targetcurve"))
top.set_ylabel("Target (dB)")
bottom.set_ylabel("Change from\nstormaudio-based (dB)")
bottom.set_xlabel("Frequency (Hz)")
bottom.set_xscale("log")
bottom.set_xlim(10, 20000)
ticks = [20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
bottom.set_xticks(ticks, [f"{t // 1000}k" if t >= 1000 else str(t) for t in ticks])
for ax in (top, bottom):
    ax.grid(True, which="both", color="#e3e7ec", lw=0.8)
    ax.legend(frameon=False, loc="lower left")
fig.tight_layout()
fig.savefig(out, dpi=150)
