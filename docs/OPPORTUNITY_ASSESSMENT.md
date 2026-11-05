# Next-opportunity assessment

Authorised as one focused desk investigation. The question: where could FoundrySide most plausibly
create user advantage, given that the current football model cycle is closed and the confirmatory
slice is preserved.

**Correction to an earlier claim of mine.** I first wrote that this environment could not reach
external sources, because three hosts failed in the fetch tool. That was wrong: DNS resolves all of
them to public addresses, and direct HTTPS from the shell returns 200 for the GitHub API, the data
provider and the Wayback CDX index. The restriction is in one tool, not in the machine, and I had
generalised from it. Everything below is therefore **verified by direct request**, not reported.

Verified while writing this:

- `api.github.com` — HTTP 200; the last five workflow runs are all green, including
  https://github.com/the-last-debugger/FoundrySide/actions/runs/41845299601
- `football-data.co.uk` — HTTP 200 for **22 division codes** in 2024/25
- `web.archive.org` CDX — HTTP 200, returning snapshot records: the route I recommended retrying is
  alive

---

## Candidate 1 — thinner and lower divisions from the existing source

**Mechanism.** Less-visited leagues attract less sharp money and thinner books; margins and
mispricing tend to be larger where the market is smaller. If any inefficiency exists in football
price data, it is more likely there than in the eight major divisions already tested.

**Licence — not established, and the evidence points against reuse.** The provider is free to
download and describes itself as a portal for analysis, but its footer reads "© Football-Data.
Liability Disclaimer. All Rights Reserved." There is no licence statement, no grant of redistribution
and no explicit permission to republish. So:

- **File availability is verified** — HTTP 200, 13,610 fixtures parsed in memory for the thirteen additions;
- **permission to redistribute or publish derived data is not established**, and "All Rights
  Reserved" is contrary to it;
- internal analysis of an already-held corpus is how this project has treated the source throughout,
  and that reading is **not a legal opinion** (`PROPOSAL.md` §3; P-03 is the open item for publication).

I should not have written "licence-identical" in the earlier draft. Availability and permission are
different facts, and only the first is established.

**Data and access — verified.** The provider serves all **22** of these codes for 2024/25, each a
HEAD 200 in the same `mmz4281/<season>/<league>.csv` format with closing odds:

`E0 E1 E2 E3 EC SC0 SC1 SC2 SC3 D1 D2 I1 I2 SP1 SP2 F1 F2 N1 B1 P1 T1 G1

**G1 is a separate question, and it is excluded unresolved.** Twenty-two codes respond, eight are
already held, so fourteen are not held - but the proposed set is thirteen. The missing one is G1
(Greece), and the honest account is that it was omitted from the coverage probe rather than judged
unsuitable: no odds-coverage measurement exists for it, and availability alone (HTTP 200) does not
establish that it can support the metric. It is recorded as an **unresolved exclusion**, and the
authorisation puts it explicitly out of scope. Not in the corpus and eligible for this test are
different claims, and only the first is established for G1.`

The corpus currently uses eight (E0, D1, E1, F1, I1, N1, P1, SP1). Thirteen are untapped. Counts are
from files read **in memory** across the three pilot seasons; no file was stored, merged or added to
the corpus.

| Division | Fixtures (3 pilot seasons) | 1X2 odds | O/U 2.5 odds |
| --- | --- | --- | --- |
| E2 | 1,656 | 99.7% | 99.7% |
| E3 | 1,656 | 99.9% | 99.9% |
| EC | 1,535 | 99.9% | 99.9% |
| I2 | 1,140 | 99.9% | 99.9% |
| SP2 | 1,386 | 99.9% | 99.9% |
| F2 | 1,140 | 100.0% | 100.0% |
| D2 | 918 | 100.0% | 100.0% |
| B1 | 918 | 100.0% | 100.0% |
| T1 | 1,142 | 97.4% | 97.4% |
| SC0 | 684 | 99.9% | 99.9% |
| SC1 | 495 | 100.0% | 100.0% |
| SC2 | 470 | 100.0% | 100.0% |
| SC3 | 470 | 100.0% | 100.0% |
| **13 divisions** | **13,610** | **99.7%** | **99.7%** |

**Correction, verified against the source files.** An earlier version listed `P1` (Portugal) as an
addition and totalled 14 divisions and 14,528 fixtures. `P1` is **already in the corpus**, so it was a
duplicate. Re-requesting each proposed division and recounting gives **13 genuinely additional
divisions, 13,610 fixtures**, and **39** division-season clusters, not 42.

That is 1.5 times the pilot (8,941) and 2.3 times the confirmatory slice (5,794), with coverage
comparable to the existing corpus. The smallest units are the Scottish lower tiers at 470 fixtures
across three seasons — about 157 a season, small enough that they must be reported per division and
never pooled silently.

**Timing fit.** Same closing prices, same T−90 caveat. No improvement in timing.

**Coverage.** Reported to include England E2/E3 and conference-level, Scotland lower, Germany 2,
Italy 2, Spain 2, France 2, Netherlands, Belgium, Portugal, Turkey, Greece. Fixture counts per season
are smaller, so the effective sample is smaller than it looks.

**Validation design.** The existing evaluation is reusable verbatim: market log loss as benchmark,
cluster-robust inference by division-season, the same 0.01-nat target. The honest test is not "does
the model do better there" but "is the *market* less efficient there" — measurable as the deviation
between the de-vigged price and realised frequency, which needs no model at all.

**Costs and risks.** Zero data cost. Risks: it is still one book family; lower divisions have fewer
fixtures and more missing prices; and the provider's coverage of those leagues may be partial.

**Why it ranks first.** It is the only candidate that is zero-cost at the file level, immediately parsable, and tests a
mechanism with prior plausibility. It is **not** licence-cleared: the provider asserts copyright,
permission to republish is not established, and any publication of derived data is P-03. It does, however, need sponsor authorisation
because it adds divisions to the corpus, which the protocol forbids without approval.

---

## Candidate 2 — genuinely new pre-decision information

**Mechanism.** Beat the price with information it has not absorbed before the cutoff.

**What was checked.** Team sheets are published 60–75 minutes before kickoff — **after** a T−90
cutoff, so lineups cannot help without changing the cutoff. The two open sources that resolve from
here (openfootball, StatsBomb) carry fixtures, results, events and lineups but **no odds and no
pre-kickoff timestamps**. No suitable timestamped price source was verified; an earlier draft described those sources as unreachable from here, which was wrong - direct HTTPS works, so the finding is absence of a verified source, not of network access.
(`SOURCE_TIMING.md`).

**Timing fit.** The binding constraint. Any candidate must be timestamped *before* the cutoff, not
merely public.

**Wayback: reachable, but not yet useful.** The CDX index returns records, so the route is alive; but
what it indexes for an odds site is page-level, not the per-fixture prices a test would need. Turning
it into a price history is a scraping and parsing job with licence questions, not a lookup.

**Verdict.** No verified zero-cost *price-timestamp* source. The blocking factor is now licence and
effort rather than reachability.

---

## Candidate 3 — other sports

**Mechanism.** A different sport may offer a data advantage football does not, or a market less
efficiently priced.

**What was checked.** Reachability is no longer the obstacle: direct HTTPS works for every host
tested. What I did **not** do is search for or verify any specific multi-sport dataset, so the honest
statement is that none was examined — not that none exists. The multi-sport ambition is
sponsor-stated; the data case is unexamined rather than disproven.

**Verdict.** Reject as a first move. It has the highest uncertainty and the largest unverified
surface, and it would require both new data and a new evaluation design.

---

## Candidate 4 — decision support

**Mechanism.** Improve the user's decision without beating the market: better available price,
abstention, clearer uncertainty.

**What is established.** The best quoted price exceeded the average quoted price by ~6.5% per
selection-snapshot
(`PRICE_INVENTORY.md`); two-book comparison saves 0.17 pp of overround and still leaves 99.1% of
fixtures negative at the better price (`BEST_PRICE.md`); filtering to confident picks *degrades*
the displayed probability (`TRACK_B.md`); movement carries nothing (`MOVEMENT_STUDY.md`).

**What is not established.** That any of it improves a user's decisions or expected value. The
apparent positive-value share is inflated by a selection effect, and no timestamp exists to show a
price is obtainable when a user acts.

**Verdict.** The evidence is real but the benefit is bounded, and the decisive test needs users —
outside this corpus and this authorisation.

---

## Ranking

| Rank | Candidate | Zero-cost now? | Needs approval? | Verdict |
| --- | --- | --- | --- | --- |
| 1 | Lower/thinner divisions, same source | verified | yes — adds divisions to the corpus | **strongest lead, not approved** |
| 2 | Timestamped pre-decision information | index reachable, no per-fixture price history | yes, for scraping or licence work | not viable at zero cost |
| 3 | Decision support | partially | yes — user study | bounded benefit, decisive test unavailable |
| 4 | Other sports | unverified | yes — new data and design | reject as a first move |

## Recommendation, stated plainly

1. **Both free checks are done and both passed** — 22 divisions available, the Wayback index
   reachable. Neither needed permission.
2. **Consider a bounded descriptive investigation on the thirteen unused divisions**, not a model extension:
   whether de-vigged prices deviate from realised frequency more in thin divisions. Cheaper and more
   decisive than another feature cycle, it needs no model to beat anything, and it answers a question
   about market efficiency rather than about our model.
3. Otherwise, **recommend not proceeding** on Track A. The evidence across twenty-four experiments
   is consistently negative, and manufacturing a twenty-fifth variant would be activity, not
   progress.

## What is not being asked for

No paid data, cloud spend, account creation, terms acceptance, third-party contact, automation, build
or real-money work. Nothing here touches the confirmatory slice.

## Proposed estimand and comparison

This section exists so the sponsor can approve or reject a specific test rather than a direction.

**Unit and data.** Division-season cluster. Fixtures from the thirteen unused divisions, three pilot
seasons: 39 clusters, 13,610 fixtures. No confirmatory fixture is read.

**The quantity.** *Market efficiency*, not model skill:

- `p` — the de-vigged closing probability for Over 2.5, proportional method as used throughout:
  `(1/over) / (1/over + 1/under)`.
- `y` — realised Over 2.5.
- **Primary metric**: market log loss, `−mean(y·log p + (1−y)·log(1−p))`. It involves no model. It
  measures how good the price itself is.
- **Secondary**: market Brier score; binned reliability and resolution of the price; and the
  calibration slope from fitting a one-parameter logistic on the price's logit.

**The comparison — both, and never only the pooled one.** Three things are reported:

1. **Every per-division result**, with fixture count and the three individual season values. This is
   the primary display, because pooling is exactly how a large division conceals a small one.
2. **A pooled weighted comparison**: fixture-weighted market log loss across the thirteen additional
   divisions against the fixture-weighted figure across the eight existing divisions, same seasons,
   same metric.
3. **The spread of the per-division differences**, so a pooled difference that hides a wide range is
   visible rather than averaged away.

The headline is the per-division table; the pooled number sits beside it as a summary, not a
substitute.

**Relevance.** A difference of 0.01 nats is used as the same descriptive scale as elsewhere in the
project — the order of magnitude of the margin. It is **not** a significance threshold here, because
this is a descriptive measurement of price quality rather than a hypothesis about an effect.

**Uncertainty — what the resampling can and cannot support.** The resampling unit is the
**division-season**: 39 clusters across the thirteen additions, 24 across the eight existing
divisions.

- **Division-level results are descriptive.** Each division contributes **three season-clusters**, and
  a bootstrap over three units does not produce a confidence interval in any useful sense. A division
  is therefore reported as a log loss, its fixture count, and its three season values shown
  individually — no interval, no significance claim.
- **The pooled comparison** resamples the 39 and 24 division-seasons and is reported with an interval.
  Even there, 39 clusters is few enough that the interval is approximate, and the report says so
  beside the number.
- **The bootstrap does not solve the small-cluster problem**, and no claim is made that it does.
  Where a division has three seasons, three is what it has.

**Dependence.** Fixtures within a division-season share a competition and a season; the cluster
bootstrap accounts for that. Cross-division pooling would not, which is why the report keeps
per-division rows alongside any aggregate.

**What this can and cannot show.** It can show whether the price is *less well calibrated* where the
market is thinner. It **cannot** show that a user could profit: that needs prices an individual could
obtain, stakes, limits and a decision rule — none of which this corpus records. A difference here is
a fact about price quality, not evidence of exploitable value or user advantage, and the report must
say so wherever it is summarised.

**Cost.** Zero data cost; the existing parser and evaluation code apply unchanged; no protocol
change, no new market family — the same Over 2.5 market, additional competitions.

**Stop condition.** If the divisions show no material difference, the result is a negative about
market thinness and the recommendation becomes not to proceed on Track A.
