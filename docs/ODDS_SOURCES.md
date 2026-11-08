# Odds from Kenyan bookmakers: what was checked, and what is possible

The request was to pull prices from Odibets, Betika, SportPesa, Betin, Betway, MozzartBet and others,
let the user choose a site, and compare. This records what is actually obtainable, because the answer
determines what the product can honestly offer.

Checked 2026-11-08, one request per site, no accounts, no login, no automation beyond a single page
fetch.

## Legality: `robots.txt`

| Site | `robots.txt` | Crawling permitted? |
| --- | --- | --- |
| Betika | `User-agent: *` / `Allow: /` | **Yes** |
| SportPesa | `User-agent: *` / `Disallow:` (empty) | Yes by robots |
| Odibets | served, no rules | Yes by robots |
| MozzartBet | served, no rules | Yes by robots |
| Betway | HTTP 523 (blocked) | **No** |

So four of five permit crawling at the robots level. Robots permission is not the whole question, but
it is the first one, and it is not the obstacle.

## Feasibility: are the prices in the page?

| Site | Response | HTML size | Price-like tokens in HTML | Verdict |
| --- | --- | --- | --- | --- |
| Betika | 200 | 9 KB | 0 | JavaScript shell; prices arrive from an API |
| Odibets | 200 | 0 KB | 0 | JavaScript shell |
| MozzartBet | 200 | 46 KB | 8 | Mostly markup; no full market list |
| SportPesa | **403** | — | — | Bot protection |
| Betway | 523 | — | — | Blocked |

**The prices are not in the server-rendered HTML on any site checked.** They are fetched by the site's
own JavaScript from an internal API. Getting them would mean either:

1. **Driving a headless browser** through each site — heavy, brittle, and it re-implements each site's
   client; and it still executes their code at our volume.
2. **Calling undocumented internal APIs** — the most fragile option, unversioned, and most likely to
   conflict with the operators' terms.
3. **Having the user supply the prices** — from the app or page already open on their phone.

## Decision

**The product does not scrape the bookmakers.** Not because the data is unavailable, but because the
available routes are either fragile, heavy, or outside the terms the project holds itself to. Two
consequences:

- The **card editor** (web Plan tab, `scripts/plan_card.py`) already accepts prices typed by the user.
  That is the lawful path to a prospective slip, and it is shipped.
- **Comparing sites** is still possible without scraping: the user enters the prices they can see for
  each site they care about, and the product compares them. The comparison logic is arithmetic; the
  acquisition is the user's.

## What would change this

A **documented, public, unauthenticated odds endpoint** with terms that permit programmatic use. If one
of these operators publishes an affiliate or partner API with a free tier, the integration becomes
straightforward — the planner already takes a fixture and three prices, so a market feed is a data
source change, not a redesign.

Until then, the honest offer is: **you supply the prices, the product does the arithmetic, and it tells
you what the comparison does and does not prove.**
