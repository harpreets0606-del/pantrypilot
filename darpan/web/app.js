// Stage-0 landing page logic: collect two birth details, call the deterministic
// engine for a real Ashtakoota score, render the breakdown, then offer the
// (gated) full sourced report as the smoke-test conversion event.

const API = location.origin.startsWith("http") ? "" : "http://localhost:8000";

// Curated cities (lat, lon, tz offset hours). DST/historical TZ is simplified
// here; the full engine resolves it precisely.
const CITIES = [
  ["Mumbai, India", 19.07, 72.87, 5.5],
  ["Delhi, India", 28.61, 77.21, 5.5],
  ["Bengaluru, India", 12.97, 77.59, 5.5],
  ["Chennai, India", 13.08, 80.27, 5.5],
  ["Kolkata, India", 22.57, 88.36, 5.5],
  ["Hyderabad, India", 17.38, 78.49, 5.5],
  ["Dubai, UAE", 25.20, 55.27, 4],
  ["New York, USA", 40.71, -74.0, -5],
  ["San Francisco, USA", 37.77, -122.42, -8],
  ["London, UK", 51.51, -0.13, 0],
  ["Toronto, Canada", 43.65, -79.38, -5],
  ["Sydney, Australia", -33.87, 151.21, 10],
  ["Singapore", 1.35, 103.82, 8],
  ["Auckland, NZ", -36.85, 174.76, 12],
];

document.querySelectorAll("select.city").forEach((sel) => {
  sel.innerHTML = '<option value="">Select city…</option>' +
    CITIES.map((c, i) => `<option value="${i}">${c[0]}</option>`).join("");
});

function personFrom(fieldset) {
  const get = (n) => fieldset.querySelector(`[name="${n}"]`).value;
  const [y, m, d] = get("date").split("-").map(Number);
  const [hh, mm] = get("time").split(":").map(Number);
  const city = CITIES[Number(get("city"))];
  return {
    name: get("name"), year: y, month: m, day: d, hour: hh, minute: mm,
    tz_offset: city[3], latitude: city[1], longitude: city[2],
  };
}

const form = document.getElementById("matchForm");
const resultEl = document.getElementById("result");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const sets = form.querySelectorAll("fieldset");
  const btn = form.querySelector("button[type=submit]");
  btn.disabled = true; btn.textContent = "Computing…";
  try {
    const res = await fetch(`${API}/api/match`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ boy: personFrom(sets[0]), girl: personFrom(sets[1]) }),
    });
    if (!res.ok) throw new Error("engine error");
    render(await res.json());
  } catch (err) {
    resultEl.classList.remove("hidden");
    resultEl.innerHTML = `<div class="scorecard"><p>Couldn't reach the engine.
      Start it with <code>uvicorn api:app</code> and try again.</p></div>`;
  } finally {
    btn.disabled = false; btn.textContent = "Reveal our compatibility";
  }
});

function flag(label, bad) {
  return `<span class="flag ${bad ? "warn" : "ok"}">${bad ? "⚠ " : "✓ "}${label}</span>`;
}

function render(data) {
  const g = data.gun_milan;
  const rows = g.kootas.map((k) => `<tr>
      <td>${k.name}</td>
      <td class="num">${k.score} / ${k.max}</td>
      <td class="note">${k.note}</td></tr>`).join("");

  resultEl.classList.remove("hidden");
  resultEl.innerHTML = `
    <div class="scorecard">
      <div class="score">${g.total}<small> / 36</small></div>
      <div class="band">${g.band}</div>
      <div class="flags">
        ${flag("Nadi", g.nadi_dosha)} ${flag("Bhakoot", g.bhakoot_dosha)}
      </div>
      <div class="moons">Person 1 Moon: <b>${data.boy.moon_nakshatra} / ${data.boy.moon_sign}</b>
        &nbsp;•&nbsp; Person 2 Moon: <b>${data.girl.moon_nakshatra} / ${data.girl.moon_sign}</b></div>
    </div>
    <table>
      <thead><tr><th>Koota</th><th class="num">Score</th><th>How it was scored</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
    <div class="capture">
      <h3>Want the full, sourced compatibility report?</h3>
      <p>A plain-language reading of what this means for your relationship — every
        claim traced to a classical source, reviewed by a verified astrologer. No fear, no upsell.</p>
      <form id="leadForm">
        <input type="email" name="email" placeholder="you@email.com" required />
        <button class="cta" type="submit">Email me the full report</button>
      </form>
    </div>`;

  resultEl.scrollIntoView({ behavior: "smooth", block: "start" });

  document.getElementById("leadForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = e.target.email.value;
    try {
      await fetch(`${API}/api/lead`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, context: `gunmilan:${g.total}` }),
      });
    } catch (_) { /* smoke test: capture intent regardless */ }
    e.target.parentElement.innerHTML =
      '<h3>Thank you 🙏</h3><p class="done">You\'re on the list — we\'ll send your sourced report shortly.</p>';
  });
}
