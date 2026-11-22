"""Geometry helpers for flow diagrams: label de-collision and ribbon paths."""

from __future__ import annotations

from dataclasses import dataclass


def spread_labels(desired: list[float], min_gap: float, lo: float, hi: float) -> list[float]:
    """Place labels as close to `desired` as possible, in order, at least `min_gap` apart.

    Uses pool-adjacent-violators on the gap-shifted positions, which gives the
    least-squares solution under the ordering constraint, then clamps into [lo, hi].
    `desired` must be sorted ascending (top-to-bottom in SVG coordinates).
    """
    n = len(desired)
    if n == 0:
        return []
    if any(b < a for a, b in zip(desired, desired[1:], strict=False)):
        raise ValueError("desired positions must be sorted ascending")
    if (n - 1) * min_gap > hi - lo + 1e-9:
        raise ValueError(f"{n} labels need {(n - 1) * min_gap:.1f}px but only {hi - lo:.1f}px available")

    # Shift so the constraint becomes "non-decreasing", then run PAVA.
    shifted = [y - i * min_gap for i, y in enumerate(desired)]
    blocks: list[list[float]] = []  # [mean, weight]
    for v in shifted:
        blocks.append([v, 1.0])
        while len(blocks) > 1 and blocks[-2][0] > blocks[-1][0]:
            m2, w2 = blocks.pop()
            m1, w1 = blocks.pop()
            blocks.append([(m1 * w1 + m2 * w2) / (w1 + w2), w1 + w2])
    fitted: list[float] = []
    for mean, weight in blocks:
        fitted += [mean] * int(weight)
    out = [z + i * min_gap for i, z in enumerate(fitted)]

    # Clamp into bounds while preserving spacing.
    for i in range(n):
        out[i] = max(out[i], lo + i * min_gap)
    for i in reversed(range(n)):
        out[i] = min(out[i], hi - (n - 1 - i) * min_gap)
    return out


def ribbon_path(x0: float, y0_top: float, y0_bot: float,
                x1: float, y1_top: float, y1_bot: float, curvature: float = 0.5) -> str:
    """SVG path for a Sankey ribbon from a vertical slice at x0 to one at x1."""
    xa = x0 + (x1 - x0) * curvature
    xb = x1 - (x1 - x0) * curvature
    f = _fmt
    return (
        f"M{f(x0)},{f(y0_top)} C{f(xa)},{f(y0_top)} {f(xb)},{f(y1_top)} {f(x1)},{f(y1_top)} "
        f"L{f(x1)},{f(y1_bot)} C{f(xb)},{f(y1_bot)} {f(xa)},{f(y0_bot)} {f(x0)},{f(y0_bot)} Z"
    )


def _fmt(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


@dataclass(frozen=True)
class Slice:
    key: str
    top: float
    bottom: float

    @property
    def height(self) -> float:
        return self.bottom - self.top

    @property
    def mid(self) -> float:
        return (self.top + self.bottom) / 2


def stack(keys: list[str], heights: list[float], top: float, gaps: list[float] | float = 0.0) -> list[Slice]:
    """Stack slices downward from `top`. `gaps[i]` is the space *before* slice i (i > 0)."""
    if isinstance(gaps, (int, float)):
        gaps = [0.0] + [float(gaps)] * (len(keys) - 1)
    if len(gaps) != len(keys) or len(heights) != len(keys):
        raise ValueError("keys, heights and gaps must align")
    out, y = [], top
    for k, h, g in zip(keys, heights, gaps, strict=True):
        y += g
        out.append(Slice(k, y, y + h))
        y += h
    return out
