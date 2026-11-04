# Jackpot feasibility — bounded desk investigation

**Status: blocked, pending a decision that is not mine.** This closes the open question rather
than leaving it as "not started". No account, contact, integration or paid access was used; the
investigation is a search and a reading of what is publicly indexed.

## What a jackpot capability would need

| Input | Why it is needed |
| --- | --- |
| **Rules** — prize tiers, rollover, void/abandoned-fixture handling, deadline | The product cannot compute a probability without knowing what counts as a win |
| **Fixture list** — which matches, which markets, kickoff windows | Jackpots fix a specific slate; a generic model is not the same object |
| **Historical outcomes** — past results per round, and whether the jackpot was won | The only way to estimate base rates or validate a display |
| **Settlement** — how a void leg is treated, whether a refund is partial | Changes the payout distribution, not just the probability |
| **Price/entry** — stake, number of entries | Needed for any expected-value statement, and often the most opaque figure |

## What was actually found

- **Press coverage exists and is substantial.** Kenyan outlets report winners, prize amounts and
  record rollovers ([The Standard](https://thestandard.ke/author/356/sportpesa),
  [The Star](https://www.the-star.co.ke/opinion/columnists/2018-09-30-ex-aspirant-wins-sh2087-million-sportpesa-jackpot)).
  This establishes that jackpots are publicly discussed, not that their mechanics are published in
  a reusable form.
- **No structured historical dataset appeared in this search.** Winners are reported as news, not
  as per-round records with fixture lists and outcomes. A dataset sufficient to estimate base rates
  was not located.
- **Operator terms were not verified.** Whether a given operator publishes rules in a form that
  permits automated access and reuse is exactly the kind of question that requires reading their
  terms, and possibly accepting them — which is an approval boundary, not a research step.

## Why this is blocked rather than negative

It is not that jackpots are unimplementable. It is that three things are missing and each has a
different owner:

1. **Rules and settlement text** — likely published by operators, but reading them under their
   terms is a decision for the sponsor, not a fetching exercise.
2. **A history of rounds** — not available in structured form from the search performed; would need
   either an operator's archive or a legal source that republishes it.
3. **Entry pricing** — often not published at all, which alone would prevent any expected-value
   statement.

## What would unblock it

Any **one** of these, in order of cost:

| Route | What it would take | Who decides |
| --- | --- | --- |
| Read operator rules | Acceptance of their terms; no account needed if the page is open | Sponsor |
| Use a regulator's published rules | Identify whether the Kenyan regulator publishes licence conditions and game rules | Research, then sponsor if terms apply |
| Estimate from press only | Not possible — press gives winners and amounts, not per-round fixtures and outcomes | — |

Until one of those happens, a jackpot capability can be described honestly as **arithmetic and
disclosure** — "this is what a 14-leg combination at these prices implies, and this is why the
probability is tiny" — with no claim about observed base rates. That is a weaker product than a
validated one, and the difference should be visible to a user.

## What this does not say

- That jackpots are unfair or unprofitable; no evidence either way was gathered.
- That the data does not exist; it says a structured, reusable form was not located in this search.
- That the rules are secret; it says their terms were not examined under this authorisation.
