# Lead triage

Written under the day-pass autonomy. Each open lead is judged by one question: could a result change a
concrete product or research decision?

| Lead | Decision it could change | Verdict | Reopen if |
| --- | --- | --- | --- |
| **Dispersion study** (amended protocol A1) | Whether the "better quote" claim is arithmetic or dispersion | **Keep, do not block.** With `K` unknown the test is weak; its value is now modest, not decisive | It is approved and run, or a timestamped source arrives |
| **Market-companion assessment** | Nothing that the product spec does not already settle | **Close.** It would restate `STRATEGIC_ASSESSMENT.md` and `PRODUCT_DIRECTION.md` | A new market or a real user study is authorised |
| **Jackpot empirical work** | Whether pool products can be analysed at all | **Close** — re-checked 2026-11-05: the Kenyan operator pages returned HTTP 200 but only 2–10 KB of shell HTML with no rules text, being script-rendered behind an age gate; no static, licence-clear rules document was found | A static rules document and a per-round payout history become available without accepting terms or creating an account |
| **Timestamped price source** | Whether any price is obtainable when a user acts | **Close, with a narrower reopening path** — re-checked 2026-11-05: the Wayback CDX index returns only section-level captures for odds portals, not per-match price history; BetExplorer serves league pages with odds and dates and its robots file permits most paths, but the site presents an age gate and its terms do not clearly license bulk reuse | A licensed or explicitly-permitted per-match feed, or a narrow attributed manual check of a handful of matches |
| **Multi-sport extension** | Whether the methods generalise | **Close as empirical** — no held data; keep as an ambition | A lawful dataset for another sport is authorised |
| **Track A / prediction edge** | Whether a forecast can beat the price | **Closed** (`CONCLUSION.md`) | A genuinely new information mechanism appears |

## Judgement on the dispersion study

**Completing it can still change a decision, but a smaller one than when it was proposed.** It decides
whether the product may describe the quote gap as dispersion or must describe it as arithmetic. That is
a real wording decision with a real user-facing consequence. It is not, however, worth stalling product
work: with `K` unknown the test is weak, and the product can ship with the honest framing either way —
"the highest recorded quote is above the average recorded quote" — which is true under both outcomes.

**Recommendation:** keep it queued behind product work, run it once approved, and do not let it gate the
build.

## What this frees

Three leads that were ceremony rather than questions are now closed with reasons, and their reopening
conditions are recorded. What remains active is the product build itself.

## Re-check under the public-data permission

On 2026-11-05 the sponsor permitted free, lawful public sources without account, payment or contact.
Both closed leads were re-examined against that permission, and the results are recorded above rather
than left as a blanket prohibition.

- **Timestamped odds.** `https://web.archive.org/cdx/search/cdx?url=oddsportal.com/soccer/*` returned
  HTTP 200 but only section-level captures (`/soccer/`), not per-match price snapshots. A BetExplorer
  league page returned 155 KB of HTML with odds and dates and its `robots.txt` disallows only a few
  paths — but the page presents an age-verification gate, and the site's terms do not clearly license
  bulk reuse. Neither is a bulk, price-history source.
- **Jackpot rules.** `betika.com/en-ke/jackpot` and `sportpesa.co.ke/jackpot` returned HTTP 200 with
  9.9 KB and 1.9 KB of shell HTML respectively, containing no rules text: both are script-rendered and
  gated. Obtaining the rules would require interactive acceptance of terms, which is outside the
  permission.

**Conclusion unchanged, but the reasons are now specific and the reopening conditions are narrow.**
