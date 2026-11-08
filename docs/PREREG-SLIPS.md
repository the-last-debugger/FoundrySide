# Pre-registration — daily slip selection and monitoring

Written before the rules were evaluated on forward seasons.

## Question

Can a fixed, pre-declared rule produce one slip per match-day that can be monitored honestly, and does
any rule show a persistent advantage?

## Design

- **Rules are declared in advance** (five of them), each producing at most one slip per match-day.
- **Legs** are outcomes of fixtures on that day; a leg's price is the recorded closing quote.
- **Two price bases are reported for every rule**: the best recorded quote and the market-average quote.
  The difference is the selection effect measured in E20, and reporting only the best would flatter
  every rule.
- **Split**: rules are evaluated on seasons 2020/21–2022/23 (train) and separately on 2023/24–2026/27
  (forward). The forward seasons are not used to choose anything.
- **Uncertainty**: a bootstrap over match-days, 2,000 draws, for the mean net of each rule.

## The five rules

| Rule | Selection |
| --- | --- |
| R1 | The day's most probable outcome, single |
| R2 | The same, restricted to prices 1.60–2.20 |
| R3 | The same, restricted to prices 2.20–3.50 |
| R4 | The two most probable outcomes, double |
| R5 | The three most probable outcomes, accumulator |

## Decision rule, fixed in advance

A rule is treated as showing a **persistent advantage** only if the forward mean is positive and its
bootstrap interval excludes zero on both price bases. Anything less is reported as noise, and no rule is
presented as profitable.

If no rule qualifies — the expected outcome given 27 prior experiments — the daily runner still runs,
because a monitored record has value even when the selection has no edge: it measures the market's
calibration and it prevents after-the-fact storytelling.

## Monitoring

Each slip is written to `var/slips.jsonl` **before** the fixtures are played, with its legs, prices,
implied probabilities and rationale. Settlement happens when results appear in the corpus. The monitor
reports hit rate and the gap between the market-implied probability and the realised frequency.

## What this cannot establish

- Anything about today's fixtures: the corpus is historical, and results arrive after the fact.
- An edge from a short sample. With roughly 600 forward days per rule, a few percentage points is noise.
- That a recorded quote was obtainable.

## Stop condition

One report, one commit. The runner continues on a schedule; the rule set does not change without a new
pre-registration.
