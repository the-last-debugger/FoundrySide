/* FoundrySide — offline engine and interface.
 *
 * This is a JavaScript port of the parts of app/engine.py the app needs: proportional de-vig, the
 * per-book market view, the matched-upside structure comparison, and a conservative slip. It is a
 * port, not a second implementation of the research: the constants (same-match dependence, margin
 * handling) come from the Python engine's documented decisions.
 *
 * Data ships in assets/fixtures.json. No network, no accounts, no bets.
 */
"use strict";

const OUTCOMES = ["H", "D", "A"];
const CROSS_MATCH_DEPENDENCE = 1.0;
let DATA = null;
let FIXTURES = [];
let BY_KEY = new Map();

const $ = (id) => document.getElementById(id);
const pct = (v, d = 1) => (v === null || v === undefined) ? "—" : (Number(v) * 100).toFixed(d) + "%";
const fmt = (v, d = 2) => (v === null || v === undefined) ? "—" : Number(v).toFixed(d);

function devig(odds) {
  const inv = odds.map(o => 1 / o);
  const total = inv.reduce((a, b) => a + b, 0);
  return inv.map(x => x / total);
}

function overround(odds) {
  return odds.reduce((a, o) => a + 1 / o, 0) - 1;
}

function load() {
  const raw = JSON.parse(FIXTURE_JSON);
  DATA = raw;
  FIXTURES = raw.fixtures;
  BY_KEY = new Map(FIXTURES.map(f => [f.k, f]));
  const options = FIXTURES.map((f, i) =>
    `<option value="${i}">${f.date} — ${f.h} v ${f.a}</option>`).join("");
  ["fixture", "fixture-m", "fixture-s"].forEach(id => { $(id).innerHTML = options; });
  $("sub").textContent = `offline · ${raw.count} fixtures · ${raw.source}`;
}

/* ---------- Assess ---------- */
function assess(fixture, outcome) {
  const idx = OUTCOMES.indexOf(outcome);
  const avg = fixture.odds.Avg || fixture.odds.Max;
  const fair = devig(avg)[idx];
  const quotes = {};
  Object.entries(fixture.odds).forEach(([name, prices]) => {
    if (name !== "Avg") quotes[name] = prices[idx];
  });
  const bestBook = Object.keys(quotes).reduce((a, b) => quotes[a] >= quotes[b] ? a : b);
  const price = quotes[bestBook];
  return {
    price, book: bestBook, quotes,
    market: fair,
    priceImplied: 1 / price,
    gap: (1 / price) - fair,
  };
}

$("go-assess").onclick = () => {
  const fixture = FIXTURES[Number($("fixture").value)];
  const outcome = $("outcome").value;
  const a = assess(fixture, outcome);
  $("assess-out").innerHTML = `
    <div class="card">
      <div class="kv">
        <div>Best recorded price <span class="tag obs">observed</span></div>
        <div>${fmt(a.price)} <span class="tag obs">${a.book}</span></div>
        <div>All recorded prices</div><div>${Object.entries(a.quotes).map(([k, v]) => k + " " + fmt(v)).join(" · ")}</div>
        <div>Market-implied probability <span class="tag est">estimated</span></div>
        <div>${pct(a.market)}</div>
        <div>Price-implied probability <span class="tag obs">observed</span></div>
        <div>${pct(a.priceImplied)}</div>
      </div>
      <div class="meter"><i style="width:${Math.min(100, a.market * 100)}%"></i></div>
      <div class="verdict">The recorded best quote is above the market average. That is a property of
      the quotes. This corpus cannot show the price was obtainable, nor that it beats fair value.</div>
      <div class="caveat">No timestamps: these are closing snapshots, not prices available when you act.</div>
      <div class="caveat">The de-vigged probability is a model of the market's belief under a
      proportional-margin assumption, not a forecast.</div>
    </div>`;
};

/* ---------- Market ---------- */
$("go-market").onclick = () => {
  const fixture = FIXTURES[Number($("fixture-m").value)];
  const rows = Object.entries(fixture.odds).map(([name, prices]) => {
    const implied = devig(prices);
    return `<tr><td class="name">${name}</td>
      <td>${prices.map(p => fmt(p)).join(" · ")}</td>
      <td>${(overround(prices) * 100).toFixed(2)}%</td>
      <td>${implied.map(p => pct(p)).join(" · ")}</td></tr>`;
  }).join("");
  const totals = fixture.totals && Object.keys(fixture.totals).length
    ? `<div class="caveat">Over/under 2.5 is also held for this fixture:
       ${Object.entries(fixture.totals).map(([k, v]) => k + " " + v.map(x => fmt(x)).join("/")).join(" · ")}</div>`
    : "";
  $("market-out").innerHTML = `
    <div class="card">
      <table><thead><tr><th>Book</th><th>Closing H · D · A</th><th>Margin</th>
      <th>Implied</th></tr></thead><tbody>${rows}</tbody></table>
      ${totals}
      <div class="caveat">A negative margin on the Max row is a synthetic artefact: it takes the best
      price for each outcome separately, which no single book offers. Not an arbitrage.</div>
    </div>`;
};

/* ---------- Structures ---------- */
function compareStructures(target, oddsList, margin = 0.05) {
  return oddsList.slice().sort((a, b) => a - b).map(odds => {
    const stake = target / (odds - 1);
    const prob = 1 / (odds * (1 + margin));
    const gross = stake * odds;
    const ev = prob * target - (1 - prob) * stake;
    return { odds, stake, gross, prob, evLoss: -ev, variance: prob * (1 - prob) * gross * gross };
  });
}

$("go-structures").onclick = () => {
  const target = Number($("target").value);
  const levels = $("odds").value.split(",").map(s => Number(s.trim())).filter(n => n > 1);
  if (!levels.length || !(target > 0)) {
    $("structures-out").innerHTML = `<div class="card"><div class="verdict warn">
      Provide a positive target and at least one odds level above 1.</div></div>`;
    return;
  }
  const rows = compareStructures(target, levels).map(s => `
    <tr><td class="name">${s.odds.toFixed(2)}×</td><td>KSh ${fmt(s.stake, 0)}</td>
    <td>KSh ${fmt(s.gross, 0)}</td><td>${pct(s.prob)}</td>
    <td>KSh ${fmt(s.evLoss, 2)}</td><td>${fmt(s.variance, 0)}</td></tr>`).join("");
  $("structures-out").innerHTML = `
    <div class="card">
      <table><thead><tr><th>Odds</th><th>At risk</th><th>Gross</th><th>Hit</th>
      <th>Expected loss</th><th>Variance</th></tr></thead><tbody>${rows}</tbody></table>
      <div class="verdict">Matched on the same net upside, structures differ in what they cost to
      hold, not in value: higher odds risk less, win less often and lose less in expectation.</div>
      <div class="caveat">Every expected loss is positive: a quoted price carries a margin.</div>
    </div>`;
};

/* ---------- Slip ---------- */
$("go-slip").onclick = () => {
  const fixture = FIXTURES[Number($("fixture-s").value)];
  const selection = $("selection-s").value;
  const stake = Number($("stake").value);
  const isTotal = selection === "O" || selection === "U";
  const market = isTotal ? "OU" : "1X2";

  let price, prob;
  if (isTotal) {
    const pair = (fixture.odds && fixture.odds.Max) ? fixture.totals.Max : null;
    if (!pair) {
      $("slip-out").innerHTML = `<div class="card"><div class="verdict warn">
        This fixture has no over/under prices.</div></div>`;
      return;
    }
    const idx = selection === "O" ? 0 : 1;
    price = pair[idx];
    prob = devig(fixture.totals.Avg || pair)[idx];
  } else {
    const idx = OUTCOMES.indexOf(selection);
    price = (fixture.odds.Max || fixture.odds.Avg)[idx];
    prob = devig(fixture.odds.Avg || fixture.odds.Max)[idx];
  }

  const gross = stake * price;
  $("slip-out").innerHTML = `
    <div class="card">
      <div class="kv">
        <div>Price <span class="tag obs">observed</span></div><div>${fmt(price)}</div>
        <div>Market-implied probability <span class="tag est">estimated</span></div>
        <div>${pct(prob)}</div>
        <div>Stake</div><div>KSh ${fmt(stake, 0)}</div>
        <div>Gross return <span class="tag hyp">hypothetical</span></div>
        <div>KSh ${fmt(gross, 0)}</div>
        <div>Net if it wins</div><div>KSh ${fmt(gross - stake, 0)}</div>
        <div>Loss if it fails</div><div>KSh −${fmt(stake, 0)}</div>
      </div>
      <div class="meter"><i style="width:${Math.min(100, prob * 100)}%"></i></div>
      <div class="caveat">One selection only. Combining legs needs a joint distribution, and this
      build does not estimate one: a same-match pair has no conditional estimate available, and
      multiplying across matches assumes independence this app cannot check.</div>
      <div class="caveat">Gross return uses recorded closing quotes, which are not shown to be
      obtainable.</div>
    </div>`;
};

/* ---------- Tabs ---------- */
document.querySelectorAll("#tabs button").forEach(btn => {
  btn.onclick = () => {
    document.querySelectorAll("#tabs button").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
    btn.classList.add("active");
    $("view-" + btn.dataset.view).classList.add("active");
  };
});

load();
