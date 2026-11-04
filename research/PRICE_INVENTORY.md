<!-- generated-by: price_inventory.py sha256=e147b2e95334 -->

# What the corpus actually contains

14,802 fixtures. This is an inventory, not an analysis: it establishes what item 2 can and cannot
support before any decision-value claim is made.

## 1X2 price families

| Family | Snapshot | Market | Fixtures with all three | Share |
| --- | --- | --- | --- | --- |
| Market average | opening | 1X2 | 14,801 | 100.0% |
| Market average | closing | 1X2 | 14,802 | 100.0% |
| Bet365 | opening | 1X2 | 14,794 | 99.9% |
| Bet365 | closing | 1X2 | 14,800 | 100.0% |
| Bet&Win | opening | 1X2 | 13,656 | 92.3% |
| Interwetten | opening | 1X2 | 10,410 | 70.3% |
| Best across books | opening | 1X2 | 14,801 | 100.0% |
| Best across books | closing | 1X2 | 14,802 | 100.0% |
| Pinnacle | opening | 1X2 | 14,793 | 99.9% |
| Pinnacle | closing | 1X2 | 14,799 | 100.0% |
| VC Bet | opening | 1X2 | 11,879 | 80.3% |
| William Hill | opening | 1X2 | 14,125 | 95.4% |

## Over/under 2.5 families

| Family | Snapshot | Fixtures with both sides | Share |
| --- | --- | --- | --- |
| Pinnacle | opening | 14,720 | 99.4% |
| Pinnacle | closing | 14,735 | 99.5% |
| Best across books | opening | 14,800 | 100.0% |
| Best across books | closing | 14,802 | 100.0% |
| Market average | opening | 14,800 | 100.0% |
| Market average | closing | 14,802 | 100.0% |

## What this changes

**There are two snapshots, not one.** The corpus carries opening and closing prices from several
books, plus `Max` (best price across the books football-data tracks) and `Avg` (their average). The
earlier best-price study used two books' closing prices because that is what it looked for; the
corpus actually supports a market-wide best-price question and a movement question.

**Per selection, the best price is genuinely better than the average** by
6.51% on average across 44,406 selection-snapshots: a user
backing one outcome can get a better price by choosing the right book. That is the tradeable
quantity.

**The three-way overround from Max columns is not tradeable.** Summing the best home, best draw
and best away price across books gives an overround 0.0526 lower than the average —
which is negative, a synthetic arbitrage, because the three best prices come from three different
books and no one offers all three at once. It is reported here only to say plainly that it must not
be read as a user opportunity.

**Movement:** the mean absolute log change in Pinnacle's home price between opening and closing is
0.0628, over 14,791 fixtures. Prices do move, so a movement-based question is
answerable; whether the movement carries information is a separate experiment.

## What this does not establish

- That a user can obtain the best price at the moment they act: the snapshot has no timestamp.
- That the best price is at an account the user can hold, or within their limits.
- That any of it turns a negative expected value into a positive one; E15's arithmetic is unchanged
  by a better price, only improved.

## What is still missing

- **No timestamps on prices.** The snapshots are labelled opening and closing, but no collection time
  is recorded, so "opening" cannot be tied to T−90 or any user action point.
- **No live or intra-day prices.** Two snapshots per book at most.
- **No limits, stakes or account terms**, so an advertised best price is not evidence of an
  obtainable one.
- **Book coverage is football-data's choice**, not the market: `Max` is the best of the books it
  tracks, not the best available anywhere.

## Limits

- Coverage differs by season and division; the shares above are pooled and a per-season split would
  show the older files carrying fewer books.
- `Max` and `Avg` are derived columns; their definitions are the provider's and are taken as given.
