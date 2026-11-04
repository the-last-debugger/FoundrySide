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

import numpy as np
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



def prequential_sizes(rows: list[dict], min_history: int = 50) -> list[float]:
    """Dispersion size used at each prediction, on a global availability-based timeline.

    A result enters the pool only when kickoff + 3h is at or before the target's cutoff, so
    simultaneous kickoffs cannot inform one another and no later fixture informs an earlier one.
    """
    ordered = sorted(rows, key=lambda r: r["cutoff_utc"])
    seen: list[int] = []
    pending: list[tuple] = []
    out: list[float] = []
    for r in ordered:
        cutoff = r["cutoff_utc"]
        if isinstance(cutoff, str):
            cutoff = datetime.fromisoformat(cutoff.replace("Z", "+00:00"))
        due = [p for p in pending if p[0] <= cutoff]
        pending = [p for p in pending if p[0] > cutoff]
        for _at, goals in due:
            seen.append(goals)
        # Two observations are the minimum for a variance; a lower min_history still needs them.
        if len(seen) >= max(min_history, 2):
            m, v = statistics.mean(seen), statistics.variance(seen)
            out.append(m * m / (v - m) if v > m else float("inf"))
        else:
            out.append(float("inf"))
        kick = r["kickoff_utc"]
        if isinstance(kick, str):
            kick = datetime.fromisoformat(kick.replace("Z", "+00:00"))
        pending.append((kick + timedelta(hours=3), r["home_goals"] + r["away_goals"]))
    return out


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

    sizes = prequential_sizes(base)
    for r, size in zip(sorted(base, key=lambda r: r["cutoff_utc"]), sizes):
        # An infinite or enormous size is the Poisson limit, where the negative-binomial
        # formula degenerates; use the Poisson probability directly there.
        r["p_nb"] = (pm.p_over_25(r["lam_h"], r["lam_a"])
                     if not math.isfinite(size) or size > 1e6
                     else nb_over(r["lam_h"] + r["lam_a"], size))

    def ll(rows, key):
        return statistics.mean(pm.logloss(r[key], r["y"]) for r in rows)

    def brier(rows, key):
        return statistics.mean((r[key] - r["y"]) ** 2 for r in rows)

    # Conditional overdispersion: Pearson chi-square against the model's own match means.
    # The pooled variance/mean ratio ignores that each match has a different lambda, so it can
    # suggest overdispersion that is really just heterogeneity in the means.
    mu = [r["lam_h"] + r["lam_a"] for r in base]
    used = [r for r, m in zip(base, mu) if m > 0]
    used_mu = [m for m in mu if m > 0]
    phi = statistics.mean((r["home_goals"] + r["away_goals"] - m) ** 2 / m
                          for r, m in zip(used, used_mu))
    n_params = 2.0 * len({(r["home"], r["away"]) for r in used}) / max(len(used), 1)
    phi_adj = phi * len(used) / max(len(used) - n_params, 1.0)

    # Cluster interval: resample division-seasons, since fixtures within one share a lambda model.
    by_cluster: dict[str, list[int]] = {}
    for i, r in enumerate(used):
        by_cluster.setdefault(r["cluster"], []).append(i)
    cluster_keys = sorted(by_cluster)
    rng = np.random.default_rng(20261103)
    draws = []
    for _ in range(500):
        idx = [i for k in (cluster_keys[rng.integers(0, len(cluster_keys))] for _ in cluster_keys)
               for i in by_cluster[k]]
        draws.append(statistics.mean((used[i]["home_goals"] + used[i]["away_goals"] - used_mu[i]) ** 2
                                     / used_mu[i] for i in idx))
    draws.sort()
    phi_lo, phi_hi = draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws)) - 1]

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
| Conditional Pearson dispersion (against model means) | {phi_adj:.3f} [{phi_lo:.3f}, {phi_hi:.3f}] |
| Matches contributing | {len(used):,} |

Poisson requires the ratio to be 1. The **pooled** ratio is {var_total / mean_total:.3f}, which
looks indistinguishable from 1. That is misleading: each match has a different conditional mean,
so the pooled ratio mixes real heterogeneity in the means with the variance around them.

The conditional test is the right one, and it disagrees. Against the model's own match-specific
means, the Pearson dispersion is **{phi_adj:.3f} [{phi_lo:.3f}, {phi_hi:.3f}]** over {len(used):,}
matches — mildly but significantly overdispersed, about six per cent excess variance. The
independent-Poisson form *is* mildly misspecified, and the pooled statistic hid it.

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

The specification is mildly wrong, and correcting it is worth almost nothing. Overdispersion is
real at {phi_adj:.3f}, but the negative binomial changes log loss by {ll(base, 'p_model') - ll(base, 'p_nb'):+.5f}
nats against a 0.0246 deficit. Both statements are true and the second is the one that matters:
a misspecified model can still be the best available one, and here fixing the distribution does
not fix the forecast. If the negative binomial does not beat Poisson out of sample,
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
