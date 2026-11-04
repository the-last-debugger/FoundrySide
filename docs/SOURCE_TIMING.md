# Source and timing investigation — timestamped multi-book prices

**Status: investigated, blocked by access terms rather than technique.** No account was created,
no paid service contacted, no page was scraped. This records what exists, what it would take to
use, and why the best-price result remains a closing-price result.

## What the current result can and cannot support

`research/BEST_PRICE.md` measures 0.17 pp of margin saved between the two books in the corpus, and
99.1% of fixtures still negative-EV at the best price. Both books are **closing** prices with no
recorded observation time. So the finding says what the dispersion was at some unspecified moment
near kickoff, not what a user could have obtained when they acted.

That gap is the whole product question for price discovery, and it cannot be closed with this
corpus.

## Routes examined

| Route | What it offers | What blocks it |
| --- | --- | --- |
| Current corpus (football-data.co.uk) | Two books' closing prices, 8 divisions, 5 seasons | No timestamps, closing only, no live dispersion |
| **Wayback Machine CDX API** | Archived snapshots of odds pages, each with a capture timestamp — potentially the only zero-cost timestamped source | **Could not be reached from this environment**: the host resolves to a non-public address here. Not verified either way |
| **OddsHarvester** ([GitHub](https://github.com/jordantete/OddsHarvester)) | An open-source scraper for oddsportal.com | It is a scraper: whether using it is permitted depends on the site's terms, which were not examined and would need a decision |
| **Apify actors** ([example](https://apify.com/sports-odds-lab/football-odds-results)) | Paid historical odds APIs, 120 bookmakers, closing lines | Paid infrastructure and an account — an approval boundary |
| **Betfair / Pinnacle APIs** | Genuine exchange prices with timestamps | Account and, for Betfair, a funded or approved application |
| **Open datasets on GitHub/Kaggle** | Some historical odds dumps exist | Kaggle requires an account; GitHub mirrors are of unknown provenance and licence, and none found with per-capture timestamps |

## Why this is blocked rather than negative

The data almost certainly exists — exchanges publish timestamped prices and books publish live
odds. What is missing is a route that is simultaneously **free, lawful, timestamped and
accessible from here**. Every candidate fails at least one:

- free and lawful, but not timestamped (current corpus);
- timestamped, but unreachable or unverified (Wayback);
- timestamped, but terms-restricted (scraping);
- lawful and timestamped, but paid or account-gated (APIs, Apify).

That is a decision about access, not a research finding, and each option has a different owner.

## What would unblock it, cheapest first

1. **Retry the Wayback index from a network where it resolves.** It costs nothing to check and
   would give timestamped snapshots with no account. This is the first thing to try, and it failed
   here for an environmental reason rather than a licensing one.
2. **Sponsor permission to accept one free-tier API's terms.** Registration is an approval
   boundary; the free tiers usually cover a small number of requests per day, which is enough to
   measure dispersion over a sample of fixtures.
3. **A paid historical feed** if the product case justifies it — the most complete option and the
   one needing the most justification.

## What the product claim should say until then

Precisely what the evidence supports: *between two closing prices, taking the better one saves
0.17 percentage points of margin.* Not: *users can obtain 0.17 pp at the moment they bet.* The
difference is the availability question, and it is the difference between a measured fact and a
marketing claim.

## Limits of this note

- Desk research, one search and one attempted fetch; not a survey of the market.
- Terms for scrapers and free tiers were not read, because reading them and accepting them is the
  decision being escalated.
- The Wayback failure is environmental and should be retried elsewhere rather than recorded as a
  dead end.
