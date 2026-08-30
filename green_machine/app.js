const state = {
  song: localStorage.getItem("gm-song") || "Add today's song",
  notes: JSON.parse(localStorage.getItem("gm-notes") || "{}"),
  player: { x: 47, y: 57 },
};

// Demo market context is intentionally marked as demo; connect it to the report JSON once the backend is ready.
const watchlist = [
  { symbol: "NVDA", price: "182.14", change: "+1.68%", direction: "up" },
  { symbol: "SPY", price: "642.68", change: "+0.31%", direction: "up" },
  { symbol: "QQQ", price: "573.94", change: "+0.54%", direction: "up" },
  { symbol: "AMD", price: "178.26", change: "-0.72%", direction: "down" },
  { symbol: "DXY", price: "98.17", change: "+0.10%", direction: "flat" },
];

const districts = {
  entrance: { eyebrow: "Park entrance", title: "Your market, with rooms for every thought.", lede: "Do not ask the park to predict for you. Use it to make your own process visible: observe, form a hypothesis, define what would change your mind, then review.", panels: [
    ["Today’s route", "1. Check market weather. 2. Visit only the two rides that matter. 3. Leave a note before the close."],
    ["Live connection", "The existing Quant Live reports are your data engine. This park is the visual layer for their output."],
    ["Daily anchor", "One song, one observation, one question. That is enough for a real daily practice.", "wide"],
  ]},
  semis: { eyebrow: "District 02", title: "Semiconductor Speedway", lede: "A place for the names you follow closely. Keep the story, the price action, the earnings date, and the invalidation in the same home.", symbols: ["NVDA", "AMD", "TSM", "AVGO"], panels: [
    ["What to look for", "Relative strength versus SOXX/QQQ, volume around key levels, and whether the whole group confirms the move."],
    ["Your task", "Write one sentence about what you believe, then one condition that would prove it wrong."],
  ]},
  macro: { eyebrow: "District 03", title: "Macro Mountain", lede: "This is the weather station. Futures, rates, FX, and scheduled events explain the terrain your stocks are moving through.", panels: [
    ["Market weather", "S&P futures: demo mode · Dollar: demo mode · 10Y: connect from your preferred source."],
    ["Dates to respect", "CPI, jobs, FOMC, Treasury auctions, and major earnings can change liquidity and price behavior."],
    ["Question before trading", "Is this stock move company-specific, sector-wide, or a reaction to the macro weather?", "wide"],
  ]},
  earnings: { eyebrow: "District 04", title: "Earnings Arcade", lede: "Earnings are events, not just dates. Build a simple event card: expectations, the key KPI, what the options market implies, and what outcome would surprise you.", symbols: ["NVDA", "CRM", "AAPL"], panels: [
    ["Event card", "Before: what is priced in? During: what changed? After: did price confirm the fundamental read?"],
    ["Risk reminder", "A strong thesis can still be a bad trade if the event risk and position size do not match."],
  ]},
  tape: { eyebrow: "District 05", title: "Tape Tunnel", lede: "This is where you slow down and observe execution. It is the bridge between loving markets and learning the real craft: liquidity, spreads, timing, and discipline.", panels: [
    ["Capture", "Time of entry, price, intended level, actual fill, exit, and a one-line reason. Your history gets useful when these are consistent."],
    ["Review", "Look for repeated behavior: chasing, entering during poor liquidity, holding through invalidation, or executing well."],
    ["Desk lens", "The existing TCA report can help you discuss slippage and execution quality like a junior quantitative trader.", "wide"],
  ]},
  signals: { eyebrow: "District 06", title: "Signal Square", lede: "Your inbox for context. Headlines, policy posts, and market chatter go here as things to verify and investigate, never as automatic signals.", panels: [
    ["Headline board", "Add a link or headline, then answer: What asset could it affect? What is already priced? What would I need to see in price or data?"],
    ["Political / policy watch", "Keep a source link and timestamp. Separate the direct claim from your interpretation and the market’s actual reaction."],
    ["Anti-noise rule", "If it does not change your thesis, event risk, or level to watch, it does not get a big place in the park.", "wide"],
  ]},
};

const dialog = document.querySelector("#district-dialog");
const title = document.querySelector("#dialog-title");
const eyebrow = document.querySelector("#dialog-eyebrow");
const lede = document.querySelector("#dialog-lede");
const content = document.querySelector("#dialog-content");
const player = document.querySelector("#player");

function renderTicker() {
  document.querySelector("#ticker-ribbon").innerHTML = watchlist.map(({ symbol, price, change, direction }) => `<div class="ticker"><b>${symbol}</b> ${price} <span class="${direction}">${change}</span></div>`).join("");
  document.querySelector("#market-weather").innerHTML = '<span class="pulse-dot"></span> Market weather: demo watchlist loaded';
}

function notePanel(name) {
  const key = name.toLowerCase().replace(/[^a-z0-9]+/g, "-");
  const value = state.notes[key] || "";
  return `<section class="panel wide"><h3>Your ${name} note</h3><textarea class="note-input" data-note="${key}" placeholder="Thesis, observation, level, or question...">${value}</textarea><button class="save-note" data-save="${key}">Save to this browser</button></section>`;
}

function symbolRows(symbols) {
  return `<section class="panel"><h3>Open a stock home</h3>${symbols.map(symbol => `<div class="symbol-row"><button data-symbol="${symbol}">${symbol}</button><span>visit →</span></div>`).join("")}</section>`;
}

function openDistrict(id) {
  const district = districts[id];
  if (!district) return;
  document.querySelectorAll(".ride-button").forEach(button => button.classList.toggle("active", button.dataset.district === id));
  eyebrow.textContent = district.eyebrow;
  title.textContent = district.title;
  lede.textContent = district.lede;
  let html = district.panels.map(([heading, body, wide]) => `<section class="panel ${wide || ""}"><h3>${heading}</h3><p>${body}</p></section>`).join("");
  if (district.symbols) html = symbolRows(district.symbols) + html;
  html += notePanel(id);
  content.innerHTML = html;
  dialog.showModal();
}

function openSymbol(symbol) {
  const key = `symbol-${symbol.toLowerCase()}`;
  eyebrow.textContent = "Stock home";
  title.textContent = `${symbol} House`;
  lede.textContent = `A single place for your interpretation of ${symbol}. The demo price above is not live data and must not be used for a trading decision.`;
  content.innerHTML = `<section class="panel"><h3>Four questions</h3><p>What is the story? What is price saying? What is the next event? What would change your mind?</p></section><section class="panel"><h3>Live-data home</h3><p>Connect this card to the Quant Live watchlist snapshot for quote, relative move, and earnings fields.</p></section>${notePanel(key)}`;
  dialog.showModal();
}

function saveNotes() { localStorage.setItem("gm-notes", JSON.stringify(state.notes)); }
function movePlayer(dx, dy) {
  state.player.x = Math.max(2, Math.min(94, state.player.x + dx));
  state.player.y = Math.max(10, Math.min(86, state.player.y + dy));
  player.style.left = `${state.player.x}%`; player.style.top = `${state.player.y}%`;
}

document.addEventListener("click", (event) => {
  const target = event.target.closest("[data-district], [data-symbol], [data-save]");
  if (!target) return;
  if (target.dataset.district) openDistrict(target.dataset.district);
  if (target.dataset.symbol) openSymbol(target.dataset.symbol);
  if (target.dataset.save) {
    const field = document.querySelector(`[data-note="${target.dataset.save}"]`);
    state.notes[target.dataset.save] = field.value.trim(); saveNotes();
    target.textContent = "Saved"; setTimeout(() => { target.textContent = "Save to this browser"; }, 900);
  }
});

document.querySelector("#dialog-close").addEventListener("click", () => dialog.close());
document.querySelector("#help-button").addEventListener("click", () => document.querySelector("#help-dialog").showModal());
document.querySelector("#help-close").addEventListener("click", () => document.querySelector("#help-dialog").close());
document.querySelector("#song-value").textContent = state.song;
document.querySelector("#song-edit").addEventListener("click", () => {
  const song = window.prompt("Today’s song", state.song === "Add today's song" ? "" : state.song);
  if (song !== null && song.trim()) { state.song = song.trim(); localStorage.setItem("gm-song", state.song); document.querySelector("#song-value").textContent = state.song; }
});
document.querySelector("#daily-review").addEventListener("click", () => openDistrict("tape"));
document.querySelector("#reset-demo").addEventListener("click", () => { localStorage.removeItem("gm-song"); localStorage.removeItem("gm-notes"); window.location.reload(); });
document.addEventListener("keydown", (event) => {
  if (dialog.open || document.querySelector("#help-dialog").open) return;
  const keys = { ArrowUp:[0,-2], w:[0,-2], ArrowDown:[0,2], s:[0,2], ArrowLeft:[-2,0], a:[-2,0], ArrowRight:[2,0], d:[2,0] };
  if (keys[event.key]) { event.preventDefault(); movePlayer(...keys[event.key]); }
});
renderTicker();
