"""Read Dirac Live .targetcurve files and evaluate them between breakpoints."""
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class Curve:
    head: list[str]  # lines up to and including BREAKPOINTS
    rows: list[str]  # breakpoint lines exactly as written: "<Hz> <dB>"
    tail: list[str]  # LOWLIMITHZ to the end of the file

    @property
    def freqs(self) -> np.ndarray:
        return np.array([float(r.split()[0]) for r in self.rows])

    @property
    def gains(self) -> np.ndarray:
        return np.array([float(r.split()[1]) for r in self.rows])

    @property
    def limits(self) -> tuple[float, float]:
        return float(self.tail[1]), float(self.tail[self.tail.index("HIGHLIMITHZ") + 1])

    def level(self, f) -> np.ndarray:
        """dB at frequency f: straight lines between breakpoints on a log-frequency axis
        (on a linear axis for the segment that starts at 0 Hz, where log is undefined)."""
        f, F, G = np.atleast_1d(np.asarray(f, float)), self.freqs, self.gains
        start = 1 if F[0] == 0 else 0
        out = np.interp(np.log(f), np.log(F[start:]), G[start:])
        if start:
            below = f < F[1]
            out[below] = np.interp(f[below], F[:2], G[:2])
        return out

    def write(self, path: Path) -> None:
        path.write_text("\n".join(self.head + self.rows + self.tail))


def read(path: Path) -> Curve:
    lines = path.read_text().split("\n")
    i, j = lines.index("BREAKPOINTS"), lines.index("LOWLIMITHZ")
    return Curve(lines[: i + 1], lines[i + 1 : j], lines[j:])
