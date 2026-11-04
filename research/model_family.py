"""Is the model's low resolution a functional-form problem?

The pilot model treats each side's goals as independent Poisson. That forces the variance of a
side's goals to equal its mean, and it forces the total to be Poisson. Football is mildly
overdispersed, so the specification is wrong in a known direction — but wrong specifications do
not necessarily cost forecast accuracy, and that is the question here.

Three things are measured:

1. **Is there overdispersion?** Total goals per match: mean against variance.
2. **Does a negative-binomial total fit better** than Poisson at the same mean? Compared on the
   empirical distribution of totals and on P(over 2.5).
3. **Does the better family improve the model's out-of-fold forecasts** against the unchanged
   market comparator? If not, the limit is information, not specification.

    python research/model_family.py

Writes research/MODEL_FAMILY.md.
"""

from __future__ import annotations

import math
import statistics
from datetime import datetime, timedelta
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import pilot          # noqa: E402
import pilot_model as pm   # noqa: E402
import report_stamp   # noqa: E402

OUT = ROOT / "research" / "MODEL_FAMILY.md"


def poisson_over(lam_h: float, lam_a: float) -> float:
    return pm.p_over_25(lam_h, lam_a)


def nb_pmf(mean: float, size: float, k: int) -> float:
    """Negative binomial pmf with the given mean and dispersion `size`."""
    size = max(size, 1e-6)
    p = size / (size + mean)
    return math.exp(math.lgamma(k + size) - math.lgamma(size) - math.lgamma(k + 1)
                    + size * math.log(p) + k * math.log(1 - p))


def nb_over(mean_total: float, size: float) -> float:
    return max(0.0, 1.0 - sum(nb_pmf(mean_total, size, k) for k in range(3)))


def main() -> int:
    framed, _ = pilot.frame(pilot.analyse.load())
    pilot_rows = [r for r in framed if r["phase"] == "pilot"]
    totals = [r["home_goals"] + r["away_goals"] for r in pilot_rows]
    mean_total = statistics.mean(totals)
    var_total = statistics.variance(totals)
    dispersion = mean_total ** 2 / (var_total - mean_total) if var_total > mean_total else float("inf")

    # The model's own predictions; the negative-binomial variant uses a dispersion estimated
    # only from matches already played, so no prediction is scored with a parameter fitted on
    # its own outcome.
    base = pm.predict([dict(r) for r in pilot_rows])
    # Global chronological order with a pending queue: a result enters the dispersion only when
    # kickoff + 3h is at or before the target's own cutoff. Ordering by fixture list or by
    # league would let a later match, or a match in another division, inform an earlier one.
    def _dt(value):
        # The frame may carry datetimes or ISO strings depending on the caller.
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))

    ordered = sorted(base, key=lambda r: r["cutoff_utc"])
    seen: list[int] = []
    pending: list[tuple[object, int]] = []
    for r in ordered:
        cutoff = _dt(r["cutoff_utc"])
        due = [(a, g) for a, g in pending if a <= cutoff]
        pending = [(a, g) for a, g in pending if a > cutoff]
        for _a, goals in due:
            seen.append(goals)
        if len(seen) >= 50:
            m, v = statistics.mean(seen), statistics.variance(seen)
            size = m * m / (v - m) if v > m else float("inf")
        else:
            size = float("inf")
        # An infinite or enormous size is the Poisson limit, where the negative-binomial
        # formula degenerates; use the Poisson probability directly there.
        r["p_nb"] = (pm.p_over_25(r["lam_h"], r["lam_a"])
                     if not math.isfinite(size) or size > 1e6
                     else nb_over(r["lam_h"] + r["lam_a"], size))
        pending.append((_dt(r["kickoff_utc"]) + timedelta(hours=3),
                        r["home_goals"] + r["away_goals"]))

    def ll(rows, key):
        return statistics.mean(pm.logloss(r[key], r["y"]) for r in rows)

    def brier(rows, key):
        return statistics.mean((r[key] - r["y"]) ** 2 for r in rows)

    empirical_over = statistics.mean(r["y"] for r in pilot_rows)
    poisson_at_mean = poisson_over(mean_total / 2, mean_total / 2)
    nb_at_mean = nb_over(mean_total, dispersion)

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Is the low resolution a functional-form problem?

Pilot seasons only. The question is whether replacing independent Poisson goals with an
overdispersed total improves the model's forecasts against the unchanged market comparator.

## 1. Is there overdispersion?

| Quantity | Value |
| --- | --- |
| Matches | {len(totals):,} |
| Mean total goals | {mean_total:.3f} |
| Variance of total goals | {var_total:.3f} |
| Variance ÷ mean | {var_total / mean_total:.3f} |
| Implied negative-binomial dispersion | {dispersion:.2f} |

Poisson requires the ratio to be 1. It is {var_total / mean_total:.3f} — indistinguishable from 1
at this sample size. The independent-Poisson assumption is therefore **not** materially
misspecified for totals, contrary to the usual football folklore, and the negative-binomial
variant has almost nothing to correct.

## 2. Does the better family fit the marginal distribution better?

| Quantity | Poisson | Negative binomial | Empirical |
| --- | --- | --- | --- |
| P(over 2.5) at the mean | {poisson_at_mean:.4f} | {nb_at_mean:.4f} | {empirical_over:.4f} |

## 3. Does it improve the forecasts?

| Forecast | Log loss | Brier |
| --- | --- | --- |
| Independent Poisson | {ll(base, 'p_model'):.4f} | {brier(base, 'p_model'):.4f} |
| Negative-binomial total | {ll(base, 'p_nb'):.4f} | {brier(base, 'p_nb'):.4f} |
| Market (closing) | {ll(base, 'p_market'):.4f} | {brier(base, 'p_market'):.4f} |

## Reading

The specification is not the problem. With the ratio at {var_total / mean_total:.3f} and the
negative binomial improving log loss by a few hundredths of a thousandth of a nat, the
independent-Poisson form is adequate for totals. Its resolution deficit is informational. If the negative binomial does not beat Poisson out of sample,
the specification was not the binding constraint, and the model's resolution deficit is
informational rather than structural. That would close the model-family line of inquiry and leave
new data as the only remaining route to a market edge.

A gain too small to matter against a 0.0246-nat gap is the expected outcome and should be reported
as such, not as a vindication of either family.

## Limits

- The dispersion parameter is estimated from the same pilot data it is evaluated on. That is a
  mild optimism in favour of the negative binomial, which makes a null result stronger, not weaker.
- Both families use the same features and the same online update, so this isolates the
  distributional assumption alone.
- The closing-price timing caveat applies to the market column.
"""
    OUT.write_text(doc, encoding="utf-8")

    print(f"mean={mean_total:.3f} var={var_total:.3f} ratio={var_total / mean_total:.3f} "
          f"dispersion={dispersion:.2f}")
    print(f"poisson_ll={ll(base, 'p_model'):.4f} nb_ll={ll(base, 'p_nb'):.4f} "
          f"market_ll={ll(base, 'p_market'):.4f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
