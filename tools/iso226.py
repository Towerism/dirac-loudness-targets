"""Equal-loudness compensation from ISO 226:2003: how much extra level each frequency needs,
relative to 1 kHz, when playback drops from a reference loudness to a quieter one.

Usage: uv run tools/iso226.py [reference_phon] [drop_dB ...]     (defaults: 85 10 20)"""
import sys

import numpy as np

# ISO 226:2003 Table 1
F = np.array([20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000,
              1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500])
AF = np.array([.532, .506, .480, .455, .432, .409, .387, .367, .349, .330, .315, .301, .288, .276, .267, .259,
               .253, .250, .246, .244, .243, .243, .243, .242, .242, .245, .254, .271, .301])
LU = np.array([-31.6, -27.2, -23.0, -19.1, -15.9, -13.0, -10.3, -8.1, -6.2, -4.5, -3.1, -2.0, -1.1, -0.4, 0.0,
               0.3, 0.5, 0.0, -2.7, -4.1, -1.0, 1.7, 2.5, 1.2, -2.1, -7.1, -11.2, -10.7, -3.1])
TF = np.array([78.5, 68.7, 59.5, 51.1, 44.0, 37.5, 31.5, 26.5, 22.1, 17.9, 14.4, 11.4, 8.6, 6.2, 4.4, 3.0,
               2.2, 2.4, 3.5, 1.7, -1.3, -4.2, -6.0, -5.4, -1.5, 6.0, 12.6, 13.9, 12.3])


def spl(phon):
    """Sound pressure level (dB) each frequency needs to sound as loud as `phon`."""
    a = 4.47e-3 * (10 ** (0.025 * phon) - 1.15) + (0.4 * 10 ** ((TF + LU) / 10 - 9)) ** AF
    return 10 / AF * np.log10(a) - LU + 94


ref = float(sys.argv[1]) if len(sys.argv) > 1 else 85.0
drops = [float(d) for d in sys.argv[2:]] or [10.0, 20.0]
# At 1 kHz phon equals dB SPL, so a drop of d phon lowers 1 kHz by exactly d dB; the extra is what's left over.
extra = [spl(ref - d) - spl(ref) + d for d in drops]
print("Hz      " + "".join(f"  -{d:g} dB" for d in drops))
for i, f in enumerate(F):
    print(f"{f:<8g}" + "".join(f"{e[i]:+8.1f}" for e in extra))
