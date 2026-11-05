"""Render a static snapshot of the product, so it can be seen without running a server.

A reviewer reading the repository cannot see what the demonstrator looks like, and a screenshot would
be an unverifiable claim. This generates a self-contained HTML page from the *actual* engine output on
a real fixture, with the same claim kinds and caveats the running product shows. Deterministic: no
clock, no random seed, so the audit can check it is current.

    python scripts/render_static.py

Writes docs/DEMO_SNAPSHOT.html
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import engine  # noqa: E402

OUT = ROOT / "docs" / "DEMO_SNAPSHOT.html"


def esc(value) -> str:
    return html.escape(str(value))


def pct(value, digits=1) -> str:
    return "—" if value is None else f"{float(value) * 100:.{digits}f}%"


def card(title: str, body: str, note: str = "") -> str:
    note_html = f'<div class="caveat">{esc(note)}</div>' if note else ""
    return f'<section class="card"><h2>{esc(title)}</h2>{body}{note_html}</section>'


def kv_rows(rows: list[tuple[str, str]]) -> str:
    return '<div class="kv">' + "".join(
        f"<div>{k}</div><div>{v}</div>" for k, v in rows) + "</div>"


def main(argv: list[str] | None = None) -> int:
    global OUT
    import argparse
    parser = argparse.ArgumentParser(description="Render a static snapshot")
    parser.add_argument("--demo", action="store_true",
                        help="use clearly-labelled synthetic fixtures instead of the held corpus")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)

    OUT = Path(args.out)
    if args.demo:
        from app import demo_data
        fixtures = demo_data.synthetic_fixtures(20)
        source = "synthetic demonstration fixtures"
    else:
        fixtures = engine.load_fixtures()
        source = "the held corpus"
    if not fixtures:
        print("no corpus available; run scripts/fetch_corpus.py or pass --demo")
        return 1

    # A deterministic pick: the first fixture of the first division.
    fixture = fixtures[0]
    view = engine.market_view(fixture)
    assessment = engine.assess_selection(fixture, "H")
    structures = engine.compare_structures(200.0, [1.5, 2.0, 3.0, 4.0, 6.0], margin=0.05)

    assess_body = kv_rows([
        ("Fixture", esc(assessment["fixture"])),
        ("Outcome", esc(assessment["outcome_label"])),
        ("Best recorded price <span class='tag obs'>observed</span>",
         f"{assessment['best_recorded_price']:.2f} <span class='tag obs'>{esc(assessment['best_book'])}</span>"),
        ("Market-implied probability <span class='tag est'>estimated</span>",
         pct(assessment["market_implied"])),
        ("Price-implied probability <span class='tag obs'>observed</span>",
         pct(assessment["price_implied"])),
    ]) + f'<div class="verdict">{esc(assessment["assessment"])}</div>' + "".join(
        f'<div class="caveat">{esc(c)}</div>' for c in assessment["caveats"])

    book_rows = "".join(
        f"<tr><td class='name'>{esc(name)}</td>"
        f"<td>{' · '.join(f'{o:.2f}' for o in q['odds'])}</td>"
        f"<td>{q['overround'] * 100:.2f}%</td>"
        f"<td>{' · '.join(pct(p) for p in q['implied'])}</td></tr>"
        for name, q in view["quotes"].items())
    market_body = (
        "<table class='grid'><thead><tr><th>Book</th><th>Closing H · D · A</th>"
        "<th>Margin</th><th>Implied probabilities</th></tr></thead>"
        f"<tbody>{book_rows}</tbody></table>"
        + "".join(f'<div class="caveat">{esc(c)}</div>' for c in view["caveats"]))

    struct_rows = "".join(
        f"<tr><td class='name'>{s['odds']:.2f}×</td><td>KSh {s['stake']:.0f}</td>"
        f"<td>KSh {s['gross']:.0f}</td><td>{pct(s['market_implied'])}</td>"
        f"<td>KSh {s['expected_loss']:.2f}</td><td>{s['variance']:,.0f}</td></tr>"
        for s in structures["structures"])
    struct_body = (
        "<table class='grid'><thead><tr><th>Odds</th><th>Stake at risk</th><th>Gross return</th>"
        "<th>Market-implied hit</th><th>Expected loss</th><th>Variance</th></tr></thead>"
        f"<tbody>{struct_rows}</tbody></table>"
        f'<div class="verdict">{esc(structures["verdict"])}</div>'
        + "".join(f'<div class="caveat">{esc(c)}</div>' for c in structures["caveats"]))

    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>FoundrySide — static snapshot</title>
<style>
 body {{ margin:0; background:#0b0d11; color:#e8ebf0;
        font:15px/1.6 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif; }}
 .wrap {{ max-width:980px; margin:0 auto; padding:32px 20px 60px; }}
 h1 {{ font-size:20px; margin:0 0 4px; }}
 .sub {{ color:#98a2b3; font-size:13px; margin-bottom:22px; }}
 .card {{ background:#151922; border:1px solid #232833; border-radius:14px;
          padding:22px 24px; margin:16px 0; }}
 h2 {{ font-size:15px; margin:0 0 12px; font-weight:620; }}
 .kv {{ display:grid; grid-template-columns:1fr auto; gap:7px 18px; }}
 .kv > div:nth-child(odd) {{ color:#98a2b3; }}
 .kv > div:nth-child(even) {{ text-align:right; font-variant-numeric:tabular-nums; font-weight:560; }}
 table.grid {{ width:100%; border-collapse:collapse; font-size:13.5px; }}
 table.grid th {{ text-align:left; color:#6b7484; font-size:11px; text-transform:uppercase;
                  letter-spacing:.6px; padding:0 8px 7px 0; }}
 table.grid td {{ padding:9px 8px 9px 0; border-top:1px solid #232833;
                  font-variant-numeric:tabular-nums; }}
 td.name {{ font-weight:600; }}
 .tag {{ font-size:10px; padding:1px 7px; border-radius:999px; border:1px solid currentColor;
         text-transform:uppercase; font-weight:600; }}
 .obs {{ color:#6cc6ff; }} .est {{ color:#d8b066; }} .hyp {{ color:#a98ce0; }}
 .caveat {{ color:#98a2b3; font-size:13px; border-left:2px solid #2f3644;
            padding-left:11px; margin:8px 0; }}
 .verdict {{ background:#101419; border:1px solid #2f3644; border-radius:9px;
             padding:12px 14px; margin:10px 0; }}
 footer {{ color:#6b7484; font-size:12.5px; border-top:1px solid #232833; margin-top:26px;
           padding-top:16px; }}
</style></head>
<body><div class="wrap">
 <h1>FoundrySide — static snapshot</h1>
 <div class="sub">Rendered from the live engine over the held corpus. Regenerate with
 <code>python scripts/render_static.py</code>; nothing here is hand-written.</div>

 {card("Assess — a standalone selection", assess_body, "Rendered from " + source + ".")}
 {card("Market — every book we hold, with its own margin", market_body)}
 {card("Structures — the same net upside at different prices", struct_body)}

 <footer>
  Prices are recorded closing quotes from a historical corpus. There are no timestamps, no account
  terms and no limits, so nothing here shows a price was obtainable when a user acts. No
  profitability, expected-value or user-advantage claim is made or implied.
 </footer>
</div></body></html>
"""
    OUT.write_text(page, encoding="utf-8")
    try:
        shown = OUT.relative_to(ROOT)
    except ValueError:
        shown = OUT
    print(f"wrote {shown} ({len(page):,} bytes) from {fixture.label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
