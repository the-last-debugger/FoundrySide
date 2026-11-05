# Lead triage

Written under the day-pass autonomy. Each open lead is judged by one question: could a result change a
concrete product or research decision?

| Lead | Decision it could change | Verdict | Reopen if |
| --- | --- | --- | --- |
| **Dispersion study** (amended protocol A1) | Whether the "better quote" claim is arithmetic or dispersion | **Keep, do not block.** With `K` unknown the test is weak; its value is now modest, not decisive | It is approved and run, or a timestamped source arrives |
| **Market-companion assessment** | Nothing that the product spec does not already settle | **Close.** It would restate `STRATEGIC_ASSESSMENT.md` and `PRODUCT_DIRECTION.md` | A new market or a real user study is authorised |
| **Jackpot empirical work** | Whether pool products can be analysed at all | **Close** — no rules or per-round history were located; the product shows arithmetic only | Rules and a payout history become available |
| **Timestamped price source** | Whether any price is obtainable when a user acts | **Close** — no lawful zero-cost source found; everything checked was gated | A free, lawful, timestamped feed appears |
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
