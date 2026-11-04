# Method note — thin-division market-efficiency measurement

Written before the run, under the sponsor's authorisation of 2026-11-04. This fixes the specification
so the result cannot be re-specified after seeing it.

## Scope, exactly as authorised

- **Thirteen additions**: `E2 E3 EC I2 SP2 F2 D2 B1 T1 SC0 SC1 SC2 SC3`.
- **Three pilot seasons**: 2021, 2122, 2223 — the same seasons as the assessment.
- **G1 (Greece) is out of scope** and recorded as an unresolved exclusion: availability was verified
  but no odds-coverage measurement exists, so it cannot be shown to support the metric.
- **Transient only**: files are read into memory and never stored, merged into the corpus, or
  retained. The confirmatory slice is not read.

## The quantity

Market efficiency, not model skill. No model is fitted anywhere in this measurement.

- `p` — the de-vigged closing probability for Over 2.5, proportional method as used throughout:
  `(1/over) / (1/over + 1/under)`, with both sides required finite and above 1.0.
- `y` — realised Over 2.5.
- **Primary**: market log loss, `−mean(y·log p + (1−y)·log(1−p))`.
- **Secondary**: Brier score; binned reliability and resolution; calibration slope from a
  one-parameter logistic on the price's logit.

## Reporting

1. **Every division separately**, with fixture count and **all three season values** individually.
   Division-level results are **descriptive**: no interval, no significance claim, no ranking of
   "most inefficient" as though it were established.
2. **A fixture-weighted pooled comparison** against the eight existing divisions on the same three
   seasons, with a division-season bootstrap interval explicitly labelled **approximate** (39 and 24
   clusters respectively).
3. **The spread of division-level differences**, so a pooled figure cannot conceal a small division.
4. The 0.01-nat gap is used as a descriptive scale, not a threshold.

## What the result would mean

- A *large* difference in price quality between thin and thick divisions would be a fact about the
  market worth reporting — and would still not be evidence of exploitable value or user advantage,
  because that needs obtainable prices, stakes and limits the corpus does not record.
- No material difference would be a negative about market thinness, and the recommendation would be
  to close Track A on evidence.

## Stop condition

The measurement runs once. The stop condition is delivery of the report; no threshold decides
whether to continue, because there is nothing to continue to without a new authorisation.
