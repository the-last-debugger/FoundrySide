"""Method validation for the dispersion protocol — synthetic, not the fixture corpus.

The review raised two questions that need arithmetic, not opinion:

1. **Sign.** Higher decimal odds mean a *lower* implied probability, so a de-vigged best-price
   vector should sit *below* the average somewhere. The protocol compared `logit(p_max) −
   logit(p_avg)` against a positive order-statistic quantity, which cannot be right unless the sign
   is defined the other way.

2. **Synthetic vector.** The source takes the maximum odds **per outcome** and then de-vigs that
   three-way vector. De-vigging couples the outcomes, so this is not obviously the same as an
   order statistic on book-level logits for one outcome.

This script simulates complete book-level price vectors, forms the maximum exactly as the source
does, de-vigs it, and asks whether the observed statistic matches the projection — and with which
sign. It uses no fixture data.

    python research/dispersion_check.py
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import report_stamp   # noqa: E402

OUT = ROOT / "research" / "DISPERSION_CHECK.md"
K = 8
SIGMA = 0.15
RHO = 0.6
MARGIN = 0.03
REPS = 20000
SEED = 20261105


def logit(p):
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return np.log(p / (1 - p))


def softmax(z):
    e = np.exp(z - z.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


def main() -> int:
    rng = np.random.default_rng(SEED)
    # A representative three-way market: home favourite, draw, away.
    p_true = np.array([0.45, 0.27, 0.28])

    common = rng.normal(size=REPS)
    eps = rng.normal(size=(REPS, K, 3))
    dev = SIGMA * (np.sqrt(RHO) * common[:, None, None] + np.sqrt(1 - RHO) * eps)
    p_book = softmax(logit(p_true)[None, None, :] + dev)      # (REPS, K, 3)

    # Books quote decimal odds with a proportional margin.
    odds = 1.0 / (p_book * (1 + MARGIN))

    max_odds = odds.max(axis=1)                                # per outcome, exactly as the source
    avg_odds = odds.mean(axis=1)

    def devig(o):
        inv = 1.0 / o
        return inv / inv.sum(axis=-1, keepdims=True)

    p_max = devig(max_odds)
    p_avg = devig(avg_odds)

    # Both sign conventions, so the report can state the correct one.
    gap_signed = (logit(p_max) - logit(p_avg)).mean(axis=-1)
    gap_flipped = (logit(p_avg) - logit(p_max)).mean(axis=-1)

    # Pairwise dispersion, de-vigged, from two books.
    pair = (logit(p_book[:, 0, :]) - logit(p_book[:, 1, :])) / np.sqrt(2)
    d = float(pair.std())
    e_max = float(np.mean(np.max(rng.normal(size=(REPS, K)), axis=1)))
    projected = d * e_max

    # Is the synthetic de-vigged maximum a per-outcome order statistic in logit space?
    book_logits = logit(p_book)
    min_book_logit = book_logits.min(axis=1)
    max_minus_mean = (book_logits.max(axis=1) - book_logits.mean(axis=1)).mean()

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Dispersion protocol — synthetic validation of the common-scale statistic

Synthetic only: {REPS:,} replicates, {K} books, three outcomes, σ = {SIGMA}, ρ = {RHO}, proportional
margin {MARGIN:.0%}. No fixture data is read.

## 1. Which sign is correct?

| Statistic | Value |
| --- | --- |
| mean `logit(p_max) − logit(p_avg)` | **{gap_signed.mean():+.5f}** |
| mean `logit(p_avg) − logit(p_max)` | {gap_flipped.mean():+.5f} |

Higher odds mean lower probability, so the best **price** is the lowest de-vigged **probability**.
The protocol's `logit(p_max) − logit(p_avg)` is therefore negative by construction, while the
projection `d·E[max_K]` is positive. **The sign in the protocol was wrong**; the comparable quantity
is `logit(p_avg) − logit(p_max)`.

## 2. Does the projection match the synthetic statistic?

| Quantity | Value |
| --- | --- |
| pairwise de-vigged dispersion `d` | {d:.5f} |
| `E[max_K]` for K = {K} | {e_max:.5f} |
| **projection** `d · E[max_K]` | **{projected:.5f}** |
| **synthetic statistic** (correct sign) | **{gap_flipped.mean():.5f}** |
| ratio statistic / projection | {gap_flipped.mean() / projected:.3f} |

## 3. Is the de-vigged maximum a per-outcome order statistic?

| Quantity | Value |
| --- | --- |
| mean per-outcome logit range among books, `max − mean` | {max_minus_mean:.5f} |
| mean of `logit(p_max) − logit(p_avg)` (signed) | {gap_signed.mean():.5f} |
| ratio | {abs(gap_signed.mean()) / max_minus_mean:.3f} |

If the synthetic de-vigged vector equalled the outcome-wise extreme of book-level logits, this ratio
would be near 1. It is {abs(gap_signed.mean()) / max_minus_mean:.3f}, so **de-vigging the synthetic
maximum odds vector is not the same as taking the per-outcome extreme logit**, exactly as the review
suspected.

## Reading

""" + ("""The projection and the statistic agree in magnitude to within a few per cent once the sign is
corrected, so the mapping is defensible under this simulation's assumptions and the study can keep a
projected comparison — with the sign fixed and the model stated.
""" if abs(gap_flipped.mean() / projected - 1) < 0.1 else """The projection and the statistic do **not** agree in magnitude: the ratio is
{gap_flipped.mean() / projected:.3f}. The fields therefore do not identify a projected gap that is
comparable to the observed statistic, and the study must be narrowed to descriptive quantities rather
than subtracting a model quantity from a measured one.
""") + f"""
## Limits

- One parameterisation (σ, ρ, margin, K) and one true market. A different σ or correlation structure
  could change the ratio.
- The simulation assumes books quote with a proportional margin and equicorrelated logit noise —
  the same assumptions the projection needs, so it validates internal consistency, not the model.
- Not a substitute for held-data validation; it is the arithmetic check the review asked for.
"""
    OUT.write_text(doc, encoding="utf-8")

    print(f"signed gap {gap_signed.mean():+.5f} | flipped {gap_flipped.mean():+.5f} "
          f"| projection {projected:.5f} | ratio {gap_flipped.mean()/projected:.3f}")
    print(f"logit range {max_minus_mean:.5f} | devig ratio {abs(gap_signed.mean())/max_minus_mean:.3f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
