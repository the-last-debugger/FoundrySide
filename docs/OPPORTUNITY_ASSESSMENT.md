# Next-opportunity assessment

Authorised as one focused desk investigation. The question: where could FoundrySide most plausibly
create user advantage, given that the current football model cycle is closed and the confirmatory
slice is preserved.

**A limitation that shapes everything below.** This environment's network reach is restricted:
`github.com`, `api.github.com` and `football-data.co.uk` all resolve to non-public addresses here,
while `raw.githubusercontent.com` resolves normally. So *verification at zero cost* is limited to raw
GitHub content. Several items below are therefore marked **reported, not verified in this session**,
and the cheapest next step may simply be to re-run the checks on a network with normal DNS.

---

## Candidate 1 — thinner and lower divisions from the existing source

**Mechanism.** Less-visited leagues attract less sharp money and thinner books; margins and
mispricing tend to be larger where the market is smaller. If any inefficiency exists in football
price data, it is more likely there than in the eight major divisions already tested.

**Data and access.** football-data.co.uk publishes lower and smaller divisions in the same
`mmz4281/<season>/<league>.csv` format with closing odds — the same source, licence and parser already
in use. **Reported, not verified this session** (DNS blocked); the existing pipeline would ingest it
unchanged.

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

**Why it ranks first.** It is the only candidate that is zero-cost, licence-identical, immediately
parsable, and tests a mechanism with prior plausibility. It does, however, need sponsor authorisation
because it adds divisions to the corpus, which the protocol forbids without approval.

---

## Candidate 2 — genuinely new pre-decision information

**Mechanism.** Beat the price with information it has not absorbed before the cutoff.

**What was checked.** Team sheets are published 60–75 minutes before kickoff — **after** a T−90
cutoff, so lineups cannot help without changing the cutoff. The two open sources that resolve from
here (openfootball, StatsBomb) carry fixtures, results, events and lineups but **no odds and no
pre-kickoff timestamps**. Timestamped price sources are blocked in this environment
(`SOURCE_TIMING.md`).

**Timing fit.** The binding constraint. Any candidate must be timestamped *before* the cutoff, not
merely public.

**Verdict.** No verified zero-cost candidate. Reject for now; the honest unblock is retrying the
Wayback CDX index from a network where it resolves, which costs nothing and needs no permission.

---

## Candidate 3 — other sports

**Mechanism.** A different sport may offer a data advantage football does not, or a market less
efficiently priced.

**What was checked.** No zero-cost, licensed, timestamped dataset was identified in this session, and
the network restriction prevents verifying any candidate directly. The multi-sport ambition is
sponsor-stated; the *data* case is unestablished.

**Verdict.** Reject as a first move. It has the highest uncertainty and the largest unverified
surface, and it would require both new data and a new evaluation design.

---

## Candidate 4 — decision support

**Mechanism.** Improve the user's decision without beating the market: better available price,
abstention, clearer uncertainty.

**What is established.** Price shopping improves the price paid by ~6.5% per selection
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
| 1 | Lower/thinner divisions, same source | yes (data), **verify on normal DNS** | yes — adds divisions to the corpus | **recommended for consideration** |
| 2 | Timestamped pre-decision information | no verified source | no, if the Wayback retry is done first | retry the free check before deciding |
| 3 | Decision support | partially | yes — user study | bounded benefit, decisive test unavailable |
| 4 | Other sports | unverified | yes — new data and design | reject as a first move |

## Recommendation, stated plainly

1. **Re-run the free checks on a network with normal DNS** — the Wayback CDX index and the provider's
   division list. Both cost nothing and both currently fail for environmental reasons, not licensing
   ones.
2. If the lower divisions are available, **authorise the efficiency measurement**, not a model
   extension: measure whether de-vigged prices deviate from realised frequency more in thin
   divisions. That is a cheaper, more decisive question than another feature cycle, and it does not
   require the model to beat anything.
3. Otherwise, **recommend not proceeding** on Track A. The evidence across twenty-three experiments
   is consistently negative, and manufacturing a twenty-fourth variant would be activity, not
   progress.

## What is not being asked for

No paid data, cloud spend, account creation, terms acceptance, third-party contact, automation, build
or real-money work. Nothing here touches the confirmatory slice.
