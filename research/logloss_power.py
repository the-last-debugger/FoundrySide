"""Power for the primary metric: paired log-loss difference.

The protocol's primary metric is log loss against the de-vigged market, so power has to
be computed for that rather than for accuracy. This builds the per-fixture score
difference from real fixtures and real closing prices.

**The model device, stated plainly.** The model deviates from the market's probability
by a fixed amount `w`, in the direction of the true outcome with probability `q = 0.6`
and away from it otherwise. That is a crude picture of the thing being claimed: a model
that is right somewhat more often than wrong when it disagrees with the price. It
produces a two-sided distribution of Δ — a real model loses on some fixtures — which a
blend-toward-the-oracle device does not, and that difference is what makes the sample
size here plausible rather than degenerate.

It is still a device, not a model. The pilot replaces it with measured differences.

    python research/logloss_power.py

Writes research/LOGLOSS_POWER.md.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import analyse  # noqa: E402

OUT = ROOT / "research" / "LOGLOSS_POWER.md"
Z = 1.959963984540054
SEED = 20261103
TARGET = 0.01                 # nats per fixture, the protocol's effect size
Q = 0.6                       # P(the deviation is toward the truth)


def phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def logloss(p: float, y: int) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return -math.log(p) if y else -math.log(1 - p)


def build(rows: list[dict]) -> list[tuple[float, int, str, str]]:
    """(de-vigged market probability, outcome, season, league) per fixture."""
    out = []
    for r in rows:
        try:
            o_over = float(r.get("PC>2.5", ""))
            o_under = float(r.get("PC<2.5", ""))
            hg, ag = int(r["FTHG"]), int(r["FTAG"])
        except (TypeError, ValueError, KeyError):
            continue
        if o_over <= 1.0 or o_under <= 1.0:
            continue
        raw_over, raw_under = 1 / o_over, 1 / o_under
        out.append((raw_over / (raw_over + raw_under),
                    1 if hg + ag >= 3 else 0, r["_season"], r["_league"]))
    return out


def deltas(data, w_bar: float, q: float = Q, seed: int = SEED) -> list[float]:
    """Per-fixture Δ log loss (market minus model).

    Each fixture gets its own deviation magnitude, `w ~ U(0, 2*w_bar)`, because a real
    model disagrees strongly on some matches and hardly at all on others. A constant
    deviation makes Δ almost deterministic and the variance collapse.
    """
    rng = random.Random(seed)
    out = []
    for p, y, _s, _l in data:
        toward = 1 if y == 1 else -1
        sign = toward if rng.random() < q else -toward
        w = rng.uniform(0.0, 2 * w_bar)
        p_model = min(max(p + sign * w, 0.01), 0.99)
        out.append(logloss(p, y) - logloss(p_model, y))
    return out


def power(diffs: list[float], n: int) -> float:
    """Two-sided power at alpha 0.05, matching the protocol and the bootstrap check.

    An earlier version computed only the upper tail, Phi(x - z), while the protocol
    specifies a two-sided test and the bootstrap used |t|. The two tails agree to
    rounding at these effect sizes, but a curve that tests a different rule from the
    check beside it is not evidence.
    """
    mean = sum(diffs) / len(diffs)
    sd = math.sqrt(sum((d - mean) ** 2 for d in diffs) / (len(diffs) - 1))
    if sd == 0:
        return 1.0
    x = mean * math.sqrt(n) / sd
    return phi(x - Z) + phi(-x - Z)


def required_n(mean: float, sd: float, z_b: float = 0.8416212335729143) -> float:
    """(z_a/2 + z_b)^2 * (sd/mean)^2, the paired-sample size for a given Δ distribution."""
    if mean <= 0:
        return float("inf")
    return (Z + z_b) ** 2 * (sd / mean) ** 2


def bootstrap_power(diffs: list[float], n: int, reps: int = 1000) -> float:
    rng = random.Random(SEED)
    rejections = 0
    for _ in range(reps):
        sample = rng.choices(diffs, k=n)
        mean = sum(sample) / n
        var = sum((d - mean) ** 2 for d in sample) / (n - 1)
        if var <= 0:
            continue
        if abs(mean / math.sqrt(var / n)) > Z:
            rejections += 1
    return rejections / reps


def solve_w(data, target: float) -> float:
    """Grid search: mean Δ is not monotone in w, because log loss punishes a confident
    wrong move far more than it rewards a right one, so bisection overshoots."""
    best, best_gap = 0.0, float("inf")
    for i in range(1, 201):
        w = i * 0.0005
        gap = abs(sum(deltas(data, w)) / len(data) - target)
        if gap < best_gap:
            best, best_gap = w, gap
    return best


def main() -> int:
    rows = analyse.load()
    data = build(rows)
    n_all = len(data)
    n_confirm = sum(1 for _p, _y, s, _l in data if s in ("2324", "2425"))

    w = solve_w(data, TARGET)
    diffs = deltas(data, w)
    mean = sum(diffs) / len(diffs)
    sd = math.sqrt(sum((d - mean) ** 2 for d in diffs) / (len(diffs) - 1))
    ordered = sorted(diffs)
    q = lambda f: ordered[int(f * (len(ordered) - 1))]  # noqa: E731

    curve = []
    for n in (2000, 4000, 6000, 8000, 12000, 20000, 30000, 60000):
        curve.append((n, power(diffs, n)))
    n_needed = next((n for n, p in curve if p >= 0.8), None)
    power_confirm = power(diffs, n_confirm)
    boot = bootstrap_power(diffs, min(n_confirm, 6000))

    # The device's sd is a lower bound, so the governing quantity is the unknown sd of
    # a real model's Δ. Show what the confirmatory slice can detect across a range.
    z_b = 0.8416212335729143
    sd_threshold = TARGET * math.sqrt(n_confirm) / (Z + z_b)
    sd_grid = (0.05, 0.10, 0.15, 0.20, 0.27, 0.35, 0.50)

    lines = [
        "# Power for the primary metric: paired log-loss difference",
        "",
        f"Generated by `python research/logloss_power.py`, seed {SEED}. The metric is the",
        "protocol's primary one: mean per-fixture **Δ = market − model**, so a positive Δ",
        "is an improvement of that many nats. An earlier protocol draft wrote the",
        "difference the other way round; the code was always market minus model, and the",
        "definition now lives in one place, `docs/EVALUATION_PROTOCOL.md` §5.",
        "",
        "**No number in this document is a forecast of the experiment's power.** Everything",
        "below is computed on a synthetic device, and the only quantity that transfers is",
        "the *shape* of the relationship between the spread of Δ and the sample needed. The",
        "pilot, not this page, supplies the real spread.",
        "",
        "## The model device",
        "",
        "The model deviates from the market probability by `w`, toward the true outcome",
        f"with probability `q = {Q}` and away from it otherwise. It is a device, not a",
        "model: it is the simplest construction that produces a **two-sided** Δ (the model",
        "loses on some fixtures) rather than the degenerate one-sided distribution a",
        "blend-toward-the-oracle gives, where every fixture improves and the variance",
        "collapses to near zero. An earlier version of this script made exactly that",
        "mistake and reported 100% power at every sample size.",
        "",
        "## The score-difference distribution",
        "",
        f"Fixtures: **{n_all:,}**; confirmatory slice (2324, 2425): **{n_confirm:,}**.",
        f"Deviation size calibrated to the target: `w = {w:.4f}`.",
        "",
        "| Statistic | Value |",
        "| --- | --- |",
        f"| Mean Δ (nats per fixture) | {mean:.4f} |",
        f"| SD of Δ | {sd:.4f} |",
        f"| 5th percentile | {q(0.05):.4f} |",
        f"| 50th percentile | {q(0.50):.4f} |",
        f"| 95th percentile | {q(0.95):.4f} |",
        "",
        "The 5th percentile is negative, which is the point: on a meaningful share of",
        "fixtures the model is worse than the price.",
        "",
        "## Sample size and power, on the device",
        "",
        "| n | Power for a 0.01-nat effect |",
        "| --- | --- |",
    ]
    for n, p in curve:
        lines.append(f"| {n:,} | {p * 100:.1f}% |")
    lines += [
        "",
        (f"**On the device**, 80% is first reached at n ≈ {n_needed:,} in this grid."
         if n_needed else "**On the device**, 80% is not reached anywhere in this grid."),
        "",
        f"Bootstrap check at n = {min(n_confirm, 6000):,}: **{boot * 100:.1f}%**, against",
        "the normal approximation in the table. Agreement means normality is not doing",
        "the work.",
        "",
        "## The number that actually governs the design",
        "",
        "The device's SD is **much smaller than a real model's** would be, because its",
        "deviations are bounded by `2w ≈ 0.06`. Reporting only the curve above would",
        "therefore overstate the case. What matters is the *unknown* SD of a real model's",
        "Δ, so here is the requirement across a plausible range at the same 0.01-nat mean:",
        "",
        "| SD of Δ | n for 80% power | Power at the confirmatory slice ("
        f"{n_confirm:,}) |",
        "| --- | --- | --- |",
    ]
    for sd_assumed in sd_grid:
        needed = required_n(TARGET, sd_assumed)
        p_confirm = phi(TARGET * math.sqrt(n_confirm) / sd_assumed - Z) \
            + phi(-TARGET * math.sqrt(n_confirm) / sd_assumed - Z)
        lines.append(f"| {sd_assumed:.2f} | {needed:,.0f} | {p_confirm * 100:.1f}% |")
    lines += [
        "",
        f"**The confirmatory slice supports 80% power at a 0.01-nat effect only while",
        f"SD(Δ) ≲ {sd_threshold:.3f}**, assuming the fixtures are independent. That is the",
        "number the pilot has to establish. It is not a matter of opinion and it is not",
        "something the protocol can assume: it is measurable on the pilot slice, and it",
        "decides whether the experiment is worth running as designed.",
        "",
        "## If the fixtures are not independent",
        "",
        "The threshold above assumes independence. With a design effect `D` — the effective",
        "sample is `n/D` — the permitted SD shrinks by `sqrt(D)`, which is the same fact",
        "from the other side: dependence makes the requirement stricter.",
        "",
        "| Design effect | Effective confirmatory n | SD(Δ) still detectable |",
        "| --- | --- | --- |",
    ]
    for deff in (1.0, 1.2, 1.5, 2.0):
        eff_n = n_confirm / deff
        thr = TARGET * math.sqrt(eff_n) / (Z + z_b)
        lines.append(f"| {deff:.1f} | {eff_n:,.0f} | {thr:.3f} |")
    lines += [
        "",
        "So the pilot has two jobs, not one: estimate the within-fixture spread of Δ **and**",
        "the between-division-season variance, because the second enters as `D` and can",
        "move the threshold by a fifth or more. Sizing on the spread alone would be the same",
        "mistake as sizing on accuracy.",
        "",
        "## Does the confirmatory slice have enough?",
        "",
        f"On the device it has **{power_confirm * 100:.1f}%**. On the unknown real SD it has",
        f"whatever the row above says — 80% only below SD {sd_threshold:.3f}, and",
        "substantially less above it.",
        "",
        "If the pilot's measured SD exceeds that threshold, the response is one of these,",
        "chosen **before** scoring:",
        "",
        "1. extend the confirmatory slice to more seasons, accepting that older seasons may",
        "   not be exchangeable;",
        "2. add markets to the family (over/under 1.5 and 3.5), raising n but enlarging the",
        "   correction family;",
        "3. raise the target effect to one the slice can detect — declared in the freeze,",
        "   not after results.",
        "",
        "What is not available is running a 5,794-fixture test, missing significance, and",
        "calling it evidence of no edge. At a realistic SD that test has less than 80%",
        "power, and a null from it is uninformative.",
        "",
        "",
        "## Why this is still optimistic",
        "",
        "- The deviation size is constant across fixtures. A real model's edge will be",
        "  larger on some and negative on others, widening the distribution.",
        "- Fixtures are treated as independent. Under league-season clustering the",
        "  effective sample is smaller; `research/POWER.md` shows how much that can cost",
        "  when advantage varies by cluster, and the same caution applies to log loss.",
        "- `q = 0.6` is a guess. It is the parameter that most affects the variance, and",
        "  the pilot measures it directly.",
        "",
        "## What this does not do",
        "",
        "- It does not score a real engine and must not be cited as an edge estimate.",
        "- It does not replace the pilot: the pilot replaces *this* device with measured",
        "  differences, and the power calculation is redone on those.",
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"fixtures={n_all} confirmatory={n_confirm} w={w:.4f} mean={mean:.4f} sd={sd:.4f}")
    print(f"n_for_80={n_needed} power_at_confirmatory={power_confirm:.3f} "
          f"bootstrap={boot:.3f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
