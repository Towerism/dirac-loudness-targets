"""Check the built packages against expected values written out by hand (not imported from build.py),
so a mistake in build.py can't hide itself. Prints only failures, and exits 1 if there are any.
Usage: python3 tools/check.py <source_package_dir> <output_root> [-v]

Check names: AC1 file set, AC2 file parses, AC3 change at key frequencies, AC4 flat cut 600 Hz-1 kHz,
AC5 same change in every speaker group, AC5b level differences between speakers kept, AC6 LCR slope limit,
AC7 header and limits unchanged, AC11 never above the source curve,
AC12 treble never rises above 4 kHz (a rise there would be a peak StormAudio's rolloff doesn't have)."""
import math, os, sys

VERBOSE = "-v" in sys.argv
SRC, OUT = [a for a in sys.argv[1:] if a != "-v"][:2]
GB = {"stormaudio-minus10dB": 4.2, "stormaudio-minus20dB": 8.3}  # packages are cuts: boost table minus GB
PKGS = {"stormaudio-minus10dB": {31: 4.2, 50: 4.2, 100: 3.0, 140: 1.5, 200: 0.2, 400: 0.0, 1250: -0.14, 2000: -0.3, 3000: -0.3, 4000: -0.3, 6300: -0.26, 8000: 0.13, 10000: 0.72, 12500: 1.0, 16000: 1.0, 20000: 1.0},
        "stormaudio-minus20dB": {31: 8.3, 50: 8.3, 100: 6.3, 140: 4.1, 200: 1.7, 400: 0.0, 1250: -0.28, 2000: -0.6, 3000: -0.6, 4000: -0.6, 6300: -0.51, 8000: 0.12, 10000: 1.06, 12500: 1.5, 16000: 1.5, 20000: 1.5}}
LCR, SUR, SUB = "LCR Cinema Target StormAudio.targetcurve", "Surround CinemaTarget StormAudio.targetcurve", "Subwoofer Cinema StormAudio.targetcurve"
fails = []

def parse(path):
    lines = open(path, newline="").read().split("\n")
    i = lines.index("BREAKPOINTS"); j = lines.index("LOWLIMITHZ")
    pts = [tuple(map(float, l.split())) for l in lines[i + 1:j]]
    return lines[:i + 1] + lines[j:], pts, (float(lines[j + 1]), float(lines[lines.index("HIGHLIMITHZ") + 1]))

def interp(pts, f):
    for (f0, g0), (f1, g1) in zip(pts, pts[1:]):
        if f0 <= f <= f1:
            t = (f - f0) / (f1 - f0) if f0 == 0 else math.log(f / f0) / math.log(f1 / f0)
            return g0 + t * (g1 - g0)
    raise ValueError(f"{f} Hz outside breakpoints")

def steps(lo, hi, per_oct):
    n = round(math.log2(hi / lo) * per_oct)
    return [f for f in (lo * 2 ** (k / per_oct) for k in range(n + 1)) if f <= hi]

names = sorted(os.listdir(SRC))
src = {n: parse(os.path.join(SRC, n)) for n in names}
for pkg, table in PKGS.items():
    d = os.path.join(OUT, pkg)
    if not os.path.isdir(d): fails.append(f"AC1 {pkg}: folder missing"); continue
    got = sorted(os.listdir(d))
    if got != names: fails.append(f"AC1 {pkg}: files {got} != {names}"); continue
    new, delta = {}, {}
    for n in names:
        try: new[n] = parse(os.path.join(d, n))
        except Exception as e: fails.append(f"AC2 {pkg}/{n}: parse error {e}"); continue
        fr = [p[0] for p in new[n][1]]
        if any(b <= a for a, b in zip(fr, fr[1:])): fails.append(f"AC2 {pkg}/{n}: frequencies not strictly increasing")
        if new[n][0] != src[n][0]: fails.append(f"AC7 {pkg}/{n}: non-breakpoint fields differ")
        delta[n] = lambda f, n=n: interp(new[n][1], f) - interp(src[n][1], f)
        lo, hi = src[n][2]
        for f, want in table.items():
            if not lo <= f <= hi: continue
            want -= GB[pkg]
            tol = 0.05 if f == 50 or f >= 1000 else 0.15
            if abs(delta[n](f) - want) > tol: fails.append(f"AC3 {pkg}/{n}: {f} Hz added {delta[n](f):+.3f}, want {want:+.2f}")
        for f in steps(600, 1000, 24):
            if abs(delta[n](f) + GB[pkg]) > 0.02: fails.append(f"AC4 {pkg}/{n}: {f:.0f} Hz change {delta[n](f):+.3f}, want {-GB[pkg]:+.1f}")
        top = min(new[n][1][-1][0], src[n][1][-1][0])
        for f in steps(10, top, 48):
            if delta[n](f) > 0.001: fails.append(f"AC11 {pkg}/{n}: {f:.0f} Hz is {delta[n](f):+.3f} dB above stormaudio-based (must be a cut)")
        low = math.inf
        for f in steps(4000, min(hi, top), 48):
            g = interp(new[n][1], f); low = min(low, g)
            if g - low > 0.1: fails.append(f"AC12 {pkg}/{n}: treble rises {g - low:.2f} dB by {f:.0f} Hz"); break
    if len(delta) != 5: continue
    for f in steps(20, 20000, 6):
        for n in names:
            lo, hi = src[n][2]
            if lo <= f <= hi and abs(delta[n](f) - delta[LCR](f)) > 0.1:
                fails.append(f"AC5 {pkg}/{n}: {f:.0f} Hz boost {delta[n](f):.3f} vs LCR {delta[LCR](f):.3f}")
    for f in (140, 200):
        for other in (SUR, SUB):
            s = interp(src[other][1], f) - interp(src[LCR][1], f)
            m = interp(new[other][1], f) - interp(new[LCR][1], f)
            if abs(s - m) > 0.05: fails.append(f"AC5b {pkg}: {other[:9]}-LCR at {f} Hz {m:+.3f} vs source {s:+.3f}")
    fs = steps(90, 250, 96); g = [interp(new[LCR][1], f) for f in fs]
    slope = max((a - b) / math.log2(f1 / f0) for f0, f1, a, b in zip(fs, fs[1:], g, g[1:]))
    if slope > 11: fails.append(f"AC6 {pkg}: LCR steepest slope {slope:.1f} dB/oct > 11")
    if VERBOSE: print(f"{pkg}: LCR steepest 90-250 Hz slope {slope:.1f} dB/oct; LCR added @50Hz {delta[LCR](50):+.2f}, @12.5k {delta[LCR](12500):+.2f}")

print("\n".join(fails) if fails else ("ALL CHECKS PASS (AC1-AC7, AC5b, AC11, AC12)" if VERBOSE else ""), end="\n" if fails or VERBOSE else "")
sys.exit(1 if fails else 0)
