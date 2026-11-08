// Exercise the browser card editor headlessly: stub the DOM, feed a card, read the output.
const fs = require("fs");
const html = fs.readFileSync("app/ui/index.html", "utf8");
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join("\n");

const elements = {
  "card-input": { value: "Arsenal | Leeds | 1.55 | 4.20 | 6.50 | Betika\nArsenal | Leeds | 1.50 | 4.30 | 6.80 | Odibets\nBayern | Mainz | 1.25 | 6.00 | 11.0\nBarcelona | Getafe | 1.40 | 4.80 | 8.00", innerHTML: "" },
  "card-go": { onclick: null },
  "card-out": { innerHTML: "" },
  "p-stake": { value: "100" },
  "p-target": { value: "10" },
};

const noop = () => {};
global.document = new Proxy({
  getElementById: (id) => (elements[id] = elements[id] || { innerHTML: '', value: '', textContent: '', onclick: null, classList: { add() {}, remove() {} }, style: {} }),
}, {
  get(target, prop) {
    if (prop in target) return target[prop];
    if (prop === 'querySelector') return () => null;
    if (prop === 'querySelectorAll') return () => [];
    if (prop === 'createElement') return () => ({ style: {}, classList: { add: noop }, appendChild: noop });
    return noop;
  },
});
global.window = { addEventListener: noop, matchMedia: () => ({ matches: false, addEventListener: noop }) };

// The page script binds tabs; ignore failures from missing DOM beyond the editor.
try { eval(scripts); } catch (e) { console.error("script error:", e.message); }

if (typeof elements["card-go"].onclick !== "function") {
  console.error("FAIL: no click handler bound");
  process.exit(1);
}
elements["card-go"].onclick();
const out = elements["card-out"].innerHTML;
if (!out || out.includes("No fixtures read")) {
  console.error("FAIL: editor produced no plan:", out.slice(0, 120));
  process.exit(1);
}
const options = (out.match(/leg[s]? at /g) || []).length;
const compared = out.includes("Book comparison");
const hasEv = out.includes("Expected net");
console.log(`options rendered: ${options}, expected-net shown: ${hasEv}`);
if (options < 1 || !hasEv || !compared) process.exit(1);
console.log("card editor plans correctly");
