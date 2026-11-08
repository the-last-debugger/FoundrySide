/* FoundrySide — offline engine and interface.
 *
 * A JavaScript port of the parts of app/engine.py the app needs: proportional de-vig, the per-book
 * market view, the matched-upside structure comparison, and a single-selection slip. It is a port,
 * and ports drift, so scripts/check_js_parity.py compares it against the Python engine fixture by
 * fixture.
 *
 * Structure: pure functions at the top (no DOM), then the interface wiring, then a bootstrap that
 * only runs in a browser. That separation is what makes the parity check possible.
 *
 * Data ships in assets/fixtures.json, embedded as data.js. No network, no accounts, no bets.
 */
"use strict";

const OUTCOMES = ["H", "D", "A"];
const CROSS_MATCH_DEPENDENCE = 1.0;

/* ================= engine ================= */

function devig(odds) {
  const inv = odds.map(o => 1 / o);
  const total = inv.reduce((a, b) => a + b, 0);
  return inv.map(x => x / total);
}

/** Round to n decimals, matching the Python engine's public contract exactly. */
function r(x, n) {
  const f = Math.pow(10, n);
  return Math.round((x + Number.EPSILON) * f) / f;
}

function overround(odds) {
  return odds.reduce((a, o) => a + 1 / o, 0) - 1;
}

/** Standalone assessment for one fixture and outcome. */
function assess(fixture, outcome) {
  const idx = OUTCOMES.indexOf(outcome);
  const avg = fixture.odds.Avg || fixture.odds.Max;
  const market = devig(avg)[idx];
  const quotes = {};
  Object.entries(fixture.odds).forEach(([name, prices]) => {
    if (name !== "Avg") quotes[name] = prices[idx];
  });
  const book = Object.keys(quotes).reduce((a, b) => (quotes[a] >= quotes[b] ? a : b));
  const price = quotes[book];
  const priceImplied = 1 / price;
  return { price, book, quotes, market: r(market, 4), priceImplied: r(priceImplied, 4),
           gap: r(priceImplied - market, 4) };
}

/** Structures matched on the same net profit. */
function compareStructures(target, oddsList, margin = 0.05) {
  return oddsList.slice().sort((a, b) => a - b).map(odds => {
    const stake = target / (odds - 1);
    const prob = 1 / (odds * (1 + margin));
    const gross = stake * odds;
    const ev = prob * target - (1 - prob) * stake;
    // Field names match app/engine.py exactly, so a parity check compares like with like.
    return { odds: r(odds, 2), stake: r(stake, 2), gross: r(gross, 2), net: r(target, 2),
             market_implied: r(prob, 4), expected_loss: r(-ev, 2),
             variance: r(prob * (1 - prob) * gross * gross, 2) };
  });
}

/** One selection: price, probability and stake arithmetic. */
function slip(fixture, selection, stake) {
  const isTotal = selection === "O" || selection === "U";
  if (isTotal) {
    if (!fixture.totals || !fixture.totals.Max) return null;
    const idx = selection === "O" ? 0 : 1;
    const price = fixture.totals.Max[idx];
    const prob = devig(fixture.totals.Avg || fixture.totals.Max)[idx];
    return { price, prob, stake, gross: stake * price, net: stake * price - stake, market: "OU" };
  }
  const idx = OUTCOMES.indexOf(selection);
  const price = (fixture.odds.Max || fixture.odds.Avg)[idx];
  const prob = devig(fixture.odds.Avg || fixture.odds.Max)[idx];
  return { price, prob, stake, gross: stake * price, net: stake * price - stake, market: "1X2" };
}


/** Latest match-day in the bundle, and its fixtures. */
function latestDay(fixtures) {
  const parsed = fixtures
    .map(f => ({ f, t: Date.parse(f.date.split("/").reverse().join("-")) }))
    .filter(x => !Number.isNaN(x.t));
  if (!parsed.length) return { date: "", day: [] };
  const newest = Math.max(...parsed.map(x => x.t));
  const day = parsed.filter(x => x.t === newest).map(x => x.f);
  return { date: day[0].date, day };
}

/** Every priced outcome on a fixture, with its best price and market-implied probability. */
function selectionsOf(fixture) {
  const probs = devig(fixture.odds.Avg || fixture.odds.Max);
  const best = fixture.odds.Max || fixture.odds.Avg;
  return OUTCOMES.map((o, i) => ({
    key: fixture.k, label: fixture.h + " v " + fixture.a, outcome: o,
    price: best[i], implied: probs[i],
  })).filter(s => s.price > 1);
}

/** Slip options for a stake and a target multiplier, on the latest match-day in the bundle. */
function planSlips(fixtures, stake, target, tolerance = 0.15, maxLegs = 3) {
  const { date, day } = latestDay(fixtures);
  if (!day.length) return { date, options: [], found: false };
  const lo = target * (1 - tolerance), hi = target * (1 + tolerance);
  const sels = day.flatMap(selectionsOf);
  const options = [];
  const add = (legs) => {
    let price = 1, implied = 1;
    for (const leg of legs) { price *= leg.price; implied *= leg.implied; }
    const gross = stake * price;
    options.push({
      n_legs: legs.length, combined_price: r(price, 3), implied_probability: r(implied, 6),
      gross_return: r(gross, 2), net_if_won: r(gross - stake, 2), loss_if_lost: r(stake, 2),
      expected_net: r(implied * gross - stake, 2),
      legs: legs.map(l => ({ fixture: l.label, selection: l.outcome,
                             price: r(l.price, 3), implied: r(l.implied, 4) })),
    });
  };
  for (let i = 0; i < sels.length; i++) {
    if (sels[i].price >= lo && sels[i].price <= hi) add([sels[i]]);
    if (maxLegs < 2) continue;
    for (let j = i + 1; j < sels.length; j++) {
      if (sels[j].key === sels[i].key) continue;
      const two = sels[i].price * sels[j].price;
      if (two >= lo && two <= hi) { add([sels[i], sels[j]]); continue; }
      if (maxLegs < 3) continue;
      for (let k = j + 1; k < sels.length; k++) {
        if (sels[k].key === sels[i].key || sels[k].key === sels[j].key) continue;
        const three = two * sels[k].price;
        if (three >= lo && three <= hi) add([sels[i], sels[j], sels[k]]);
      }
    }
  }
  options.sort((a, b) => Math.abs(a.combined_price - target) - Math.abs(b.combined_price - target));
  return { date, options: options.slice(0, 6), found: options.length > 0 };
}

/* Publish the pure surface for the parity check; harmless in a browser. */
if (typeof globalThis !== "undefined") {
  globalThis.__fs = { devig, overround, assess, compareStructures, slip, planSlips, OUTCOMES };
}

/* ================= interface ================= */

const HAS_DOM = typeof document !== "undefined";
const $ = (id) => (HAS_DOM ? document.getElementById(id) : null);
const pct = (v, d = 1) => (v === null || v === undefined) ? "—" : (Number(v) * 100).toFixed(d) + "%";
const fmt = (v, d = 2) => (v === null || v === undefined) ? "—" : Number(v).toFixed(d);

let FIXTURES = [];

function load() {
  const raw = JSON.parse(FIXTURE_JSON);
  FIXTURES = raw.fixtures;
  const options = FIXTURES.map((f, i) =>
    `<option value="${i}">${f.date} — ${f.h} v ${f.a}</option>`).join("");
  ["fixture", "fixture-m", "fixture-s"].forEach(id => { $(id).innerHTML = options; });
  $("sub").textContent = `offline · ${raw.count} fixtures · ${raw.source}`;
}

function wireUI() {
  $("go-assess").onclick = () => {
    const fixture = FIXTURES[Number($("fixture").value)];
    const a = assess(fixture, $("outcome").value);
    $("assess-out").innerHTML = `
      <div class="card">
        <div class="kv">
          <div>Best recorded price <span class="tag obs">observed</span></div>
          <div>${fmt(a.price)} <span class="tag obs">${a.book}</span></div>
          <div>All recorded prices</div>
          <div>${Object.entries(a.quotes).map(([k, v]) => k + " " + fmt(v)).join(" · ")}</div>
          <div>Market-implied probability <span class="tag est">estimated</span></div>
          <div>${pct(a.market)}</div>
          <div>Price-implied probability <span class="tag obs">observed</span></div>
          <div>${pct(a.priceImplied)}</div>
        </div>
        <div class="meter"><i style="width:${Math.min(100, a.market * 100)}%"></i></div>
        <div class="verdict">The recorded best quote is above the market average. That is a property of
        the quotes. This corpus cannot show the price was obtainable, nor that it beats fair value.</div>
        <div class="caveat">No timestamps: these are closing snapshots, not prices available when you
        act.</div>
        <div class="caveat">The de-vigged probability is a model of the market's belief under a
        proportional-margin assumption, not a forecast.</div>
      </div>`;
  };

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
      ? `<div class="caveat">Over/under 2.5 is also held: ${Object.entries(fixture.totals)
          .map(([k, v]) => k + " " + v.map(x => fmt(x)).join("/")).join(" · ")}</div>`
      : "";
    $("market-out").innerHTML = `
      <div class="card">
        <table class="grid"><thead><tr><th>Book</th><th>Closing H · D · A</th><th>Margin</th>
        <th>Implied</th></tr></thead><tbody>${rows}</tbody></table>
        ${totals}
        <div class="caveat">A negative margin on the Max row is a synthetic artefact: it takes the best
        price for each outcome separately, which no single book offers. Not an arbitrage.</div>
      </div>`;
  };

  $("p-go").onclick = () => {
    const stake = Number($("p-stake").value);
    const target = Number($("p-target").value);
    const result = planSlips(FIXTURES, stake, target, 0.15, 3);
    if (!result.found) {
      $("p-out").innerHTML = `<div class="card"><div class="verdict warn">
        No slip on ${result.date} lands near ${target}x. The market does not offer that multiplier
        from these fixtures.</div></div>`;
      return;
    }
    const cards = result.options.map(o => `
      <div class="card">
        <h3>${o.n_legs} leg${o.n_legs > 1 ? "s" : ""} at ${fmt(o.combined_price, 2)}x</h3>
        ${o.legs.map(l => `<div class="caveat">${l.fixture} - ${l.selection} at ${fmt(l.price, 2)}</div>`).join("")}
        <div class="kv">
          <div>Market-implied probability <span class="tag est">estimated</span></div>
          <div>${pct(o.implied_probability, 2)}</div>
          <div>Net if it wins <span class="tag hyp">hypothetical</span></div>
          <div>KSh ${fmt(o.net_if_won, 0)}</div>
          <div>Loss if it fails</div><div>KSh -${fmt(o.loss_if_lost, 0)}</div>
          <div>Expected net</div><div>KSh ${fmt(o.expected_net, 2)}</div>
        </div>
      </div>`).join("");
    $("p-out").innerHTML = `<div class="caveat">Match-day ${result.date}, not today's fixtures: this
      build has no fixtures feed.</div>${cards}`;
  };

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
        <table class="grid"><thead><tr><th>Odds</th><th>At risk</th><th>Gross</th><th>Hit</th>
        <th>Expected loss</th><th>Variance</th></tr></thead><tbody>${rows}</tbody></table>
        <div class="verdict">Matched on the same net upside, structures differ in what they cost to
        hold, not in value: higher odds risk less, win less often and lose less in expectation.</div>
        <div class="caveat">Every expected loss is positive: a quoted price carries a margin.</div>
      </div>`;
  };

  $("go-slip").onclick = () => {
    const fixture = FIXTURES[Number($("fixture-s").value)];
    const s = slip(fixture, $("selection-s").value, Number($("stake").value));
    if (!s) {
      $("slip-out").innerHTML = `<div class="card"><div class="verdict warn">
        This fixture has no over/under prices.</div></div>`;
      return;
    }
    $("slip-out").innerHTML = `
      <div class="card">
        <div class="kv">
          <div>Price <span class="tag obs">observed</span></div><div>${fmt(s.price)}</div>
          <div>Market-implied probability <span class="tag est">estimated</span></div>
          <div>${pct(s.prob)}</div>
          <div>Stake</div><div>KSh ${fmt(s.stake, 0)}</div>
          <div>Gross return <span class="tag hyp">hypothetical</span></div>
          <div>KSh ${fmt(s.gross, 0)}</div>
          <div>Net if it wins</div><div>KSh ${fmt(s.net, 0)}</div>
          <div>Loss if it fails</div><div>KSh −${fmt(s.stake, 0)}</div>
        </div>
        <div class="meter"><i style="width:${Math.min(100, s.prob * 100)}%"></i></div>
        <div class="caveat">One selection only. Combining legs needs a joint distribution, and this
        build does not estimate one.</div>
        <div class="caveat">Gross return uses recorded closing quotes, which are not shown to be
        obtainable.</div>
      </div>`;
  };

  document.querySelectorAll("#tabs button").forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll("#tabs button").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
      btn.classList.add("active");
      $("view-" + btn.dataset.view).classList.add("active");
    };
  });
}

/* ================= bootstrap ================= */

if (HAS_DOM) {
  load();
  wireUI();
}
