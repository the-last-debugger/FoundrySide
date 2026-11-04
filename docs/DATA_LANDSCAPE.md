# Zero-cost data landscape

Status: desk research, no data merged, confirmatory slice untouched. This records what exists,
what is actually accessible without payment or accounts, and what each source could add.

**Verification labels.** `verified` means this session fetched the URL and received the described
content with no authentication. `reported` means it is from documentation or general knowledge and
was *not* fetched here. Nothing is marked verified that was not.

---

## 1. The timing problem that decides the question

Before comparing sources, one fact constrains all of them.

The protocol predicts at **T−90**: ninety minutes before kickoff. Actual team sheets are
published roughly **60–75 minutes before kickoff** — after the cutoff. So a lineup-based feature
is *not* available at the prediction moment, no matter how good the source is. Any model that used
lineups would need a later cutoff (T−15), which is a different experiment and a different market
comparator, not an upgrade of this one.

This matters because "get lineups" is the intuitive answer to "your model lacks information". For
this protocol it is the wrong answer: the information arrives after the forecast must be made.

**What would help at T−90**: team news that leaks earlier (injury reports, press conferences,
travel squad announcements), expected-lineup aggregators, or market prices from earlier in the
week — none of which the sources below obviously provide at zero cost and with timestamps.

## 2. Candidates

| Source | Access | Contents | Adds beyond current corpus | Verified |
| --- | --- | --- | --- | --- |
| **football-data.co.uk** (current corpus) | Direct CSV, no auth, no terms page beyond attribution | Results, closing odds (1X2, O/U 2.5, AH), 22 divisions, 1993– | — | verified (already held) |
| **openfootball / football.json** | Raw GitHub JSON, no auth | Fixtures, kickoff date/time, scores, round labels; many leagues | More competitions and seasons; **no odds, no lineups** | **verified** (HTTP 200, JSON parsed) |
| **StatsBomb open data** | Raw GitHub JSON, no auth, attribution required | Events, lineups, 360 data for selected competitions | **Lineups and event detail** — but see §1: post-kickoff availability makes them unusable at T−90 | **verified** (README fetched) |
| **football-data.org** | API, **registration + API key**, free tier rate-limited | Fixtures, results, some odds on paid tiers | Not zero-cost in practice (account creation is an approval boundary) | reported |
| **API-Football / RapidAPI** | **Registration**, paid tiers | Broad coverage, odds, lineups | Gated; not authorised | reported |
| **FBref / Sports Reference** | Web scraping; ToS restricts automated collection | Rich stats, xG | Terms conflict with reuse; not zero-cost in the licence sense | reported |
| **Understat** | Web scraping, no explicit reuse licence | xG, shots | Licence unclear; scraping burden | reported |
| **Transfermarkt / worldfootball / 11v11** | Web UI only | Squads, histories | View-only; no reuse rights | reported |
| **Wikipedia / Wikidata** | API, CC BY-SA | Club and season metadata | Reference data only; no per-fixture information | reported |
| **Kaggle / DataHub mirrors** | Kaggle requires an **account**; DataHub is open | Copies of the above | Mostly duplicates; provenance usually unclear | reported |

## 3. What is actually reachable from Kenya at zero cost

The current corpus, openfootball and StatsBomb are the three that returned data without an
account, a key or a payment in this session. The rest either require registration (an approval
boundary this direction explicitly excludes) or restrict automated reuse.

I cannot verify *network-level* accessibility from Kenya from here — I can verify that the hosts
served content to this session without authentication. Latency, rate limits and any regional
blocking are untested and are recorded as untested rather than assumed.

## 4. What each source could actually change

| Question | Answer with current corpus | Would this source change it? |
| --- | --- | --- |
| More competitions/seasons? | 8 divisions, 5 seasons | openfootball: **yes**, coverage only — the information content is the same results, so the null findings likely reproduce |
| Pre-kickoff team news at T−90? | Absent | **no verified zero-cost source**; StatsBomb lineups arrive too late |
| Earlier or in-play prices? | Closing prices only | no zero-cost source found |
| Other markets (BTTS, correct score)? | 1X2, O/U 2.5, AH only | no zero-cost source found |

The honest summary: **none of the accessible sources supplies the class of information the
evidence points at.** They extend coverage, not information.

## 5. Recommendation

1. **Do not integrate.** Nothing verified here adds a pre-kickoff information class, and merging
   more results would enlarge the corpus without changing what it can support.
2. **If coverage is wanted**, openfootball is the only zero-cost, licence-clean option, and the
   expected outcome is that the E8 nulls reproduce on a wider sample — worth doing only if
   replication is the goal.
3. **If information is wanted**, the honest next step is a sponsor decision on a source that
   costs something (registration or payment), since every free route examined either lacks the
   data or restricts reuse.
4. **The T−90 constraint should be revisited before any lineup work.** A T−15 cutoff would make
   StatsBomb usable, but it changes the experiment's premise and the comparator, and that is a
   protocol decision, not a data-sourcing one.

## 6. Limits of this report

- One session of desk research; sources not fetched are labelled `reported` and may be out of date.
- Licences were read only at the level of "what the page says"; this is **not** a legal opinion.
- No sample was downloaded or stored, so nothing here is validated on data.
- Kenya-specific access, rate limits and terms of use remain untested.
