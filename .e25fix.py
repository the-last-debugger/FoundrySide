"""One-off: separate the two implied-probability quantities and fix the EV example."""
from pathlib import Path

p = Path("research/stake_structures.py")
t = p.read_text(encoding="utf-8")

# 1. Compute both quantities explicitly, with names that cannot be confused.
t = t.replace(
    """        implied_mean = statistics.mean(x["prob"] for x in band)
        realised = sum(1 for x in band if x["won"]) / len(band)
        centre = statistics.median(x["price"] for x in band)
        s = structures_for(centre, margin, TARGET_NET)
        realised_ev = realised * centre - 1.0
        table.append({"low": low, "high": high, "n": len(band), "centre": centre,
                      "implied": implied_mean, "realised": realised, "realised_ev": realised_ev,
                      "stake": s["stake"], "downside": s["downside"],
                      "variance": s["variance"], "prob": s["prob"]})""",
    """        # Two different quantities, deliberately named apart:
        #   implied_mean      - the mean of each selection's own de-vigged probability
        #   implied_at_median - the implied probability AT the band's median price
        implied_mean = statistics.mean(x["prob"] for x in band)
        realised = sum(1 for x in band if x["won"]) / len(band)
        centre = statistics.median(x["price"] for x in band)
        s = structures_for(centre, margin, TARGET_NET)
        realised_ev = realised * centre - 1.0
        table.append({"low": low, "high": high, "n": len(band), "centre": centre,
                      "implied_mean": implied_mean, "implied_at_median": s["prob"],
                      "realised": realised, "realised_ev": realised_ev,
                      "stake": s["stake"], "downside": s["downside"],
                      "variance": s["variance"]})""",
    1,
)

# 2. Table: show both, and the median price the EV refers to.
t = t.replace(
    """| Odds band | Selections | Median price | Stake needed | Lost if it fails | Market-implied hit | Realised hit (95% cluster) | Realised EV at that price |
| --- | --- | --- | --- | --- | --- | --- | --- |""",
    """Two implied quantities appear below and they are **not interchangeable**: the mean of each
selection's own de-vigged probability, and the implied probability at the band's median price. The
table gives both, because the first is the right comparator for a realised rate and the second is the
price a single stake would actually face.

| Odds band | Selections | Median price | Stake needed | Lost if it fails | Mean implied | Implied at median | Realised hit (95% cluster) | Realised EV at median |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |""",
    1,
)

t = t.replace(
    """        f"{row['realised']*100:.1f}% [{lo*100:.1f}, {hi*100:.1f}] | "
        f"{row['realised_ev']*100:+.1f}% |\"""",
    """        f"{row['implied_mean']*100:.1f}% | {row['implied_at_median']*100:.1f}% | "
        f"{row['realised']*100:.1f}% [{lo*100:.1f}, {hi*100:.1f}] | "
        f"{row['realised_ev']*100:+.2f}% |\"""",
    1,
)
t = t.replace(
    """        f"KSh {row['stake']:.0f} | KSh {row['downside']:.0f} | {row['prob']*100:.1f}% | \"""",
    """        f"KSh {row['stake']:.0f} | KSh {row['downside']:.0f} | \"""",
    1,
)

# 3. Calibration bullets compare the realised rate with the MEAN implied probability.
t = t.replace(
    """        f"- **{row['low']:.1f}–{row['high']:.1f}**: implied {row['implied']*100:.1f}%, realised \"""",
    """        f"- **{row['low']:.1f}–{row['high']:.1f}**: mean implied {row['implied_mean']*100:.1f}%, realised \"""",
    1,
)
t = t.replace(
    """        + ("consistent with the implied probability." if lo <= row['implied'] <= hi""",
    """        + ("consistent with the mean implied probability." if lo <= row['implied_mean'] <= hi""",
    1,
)

# 4. The worked example must use the computed figures, not a rounded price.
t = t.replace(
    """`realised hit x median price - 1` is what a flat-stake backer would have earned in each band, before
stake limits and with no price shopping. Every band is **negative**, including the short one where the
realised rate runs above the implied probability: at a median price near 1.55, a 63.3% hit rate returns
about -1.9%. A calibration pattern that does not survive its own margin is not an opportunity, and
here the margin is larger than the departure.""",
    """`realised hit x median price - 1` is what a flat-stake backer would have earned in each band, before
stake limits and with no price shopping. Every band is **negative**, including the short one where the
realised rate runs above the mean implied probability. The figure is computed from the band's own
median price and its own realised rate, so the two cannot drift apart:

""" + "\n".join(
        f"- **{row['low']:.1f}-{row['high']:.1f}**: median price {row['centre']:.2f}, realised "
        f"{row['realised']*100:.2f}%, EV {row['realised_ev']*100:+.2f}%"
        for row in table) + """

A calibration pattern that does not survive its own margin is not an opportunity, and here the margin
is larger than the departure.""",
    1,
)

p.write_text(t, encoding="utf-8")
print("two implied quantities separated; EV example computed")
