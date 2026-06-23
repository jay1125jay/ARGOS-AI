  let autoRunning = false;

async function loadData() {
  const res = await fetch("/api/status");
  const data = await res.json();

  const portfolio = data.portfolio || {};
  const report = data.report || {};
  const analytics = data.analytics || {};
  const news = data.news || {};
  const macro = data.macro || {};
  const ai = data.ai || {};
  const backtest = data.backtest || {};
  const execution = data.execution || {};
  const chart = data.chart || {};
  const health = data.health || {};
  const positionsData = data.positions || { positions: [] };
  const positions = positionsData.positions || [];
  const results = data.market?.results || [];

  setText("startBalance", portfolio.start_balance ?? 0);
  setText("currentBalance", formatNumber(portfolio.current_balance ?? 0));
  setText("totalReturn", (portfolio.total_return_pct ?? 0) + "%");
  setText("openPositions", positions.length);

  setText("healthStatus", health.status ?? "-");
  setText("healthFilesOk", health.files_ok ?? 0);
  setText("healthFilesTotal", health.files_total ?? 0);

  setText("total", report.total_trades ?? 0);
  setText("wins", report.wins ?? 0);
  setText("losses", report.losses ?? 0);
  setText("winRate", (report.win_rate ?? 0) + "%");
  setText("pnl", formatNumber(report.total_pnl ?? 0));

  setText("profitFactor", analytics.profit_factor ?? 0);
  setText("avgWin", analytics.avg_win ?? 0);
  setText("avgLoss", analytics.avg_loss ?? 0);

  setText("newsMode", news.mode ?? "-");
  setText("newsSentiment", news.market_sentiment ?? "-");
  setText("newsRisk", news.risk_level ?? "-");

  setText("macroMode", macro.mode ?? "-");
  setText("macroRegime", macro.market_regime ?? "-");
  setText("macroDxy", macro.dxy_status ?? "-");
  setText("macroRate", macro.rate_risk ?? "-");

  setText("aiMode", ai.mode ?? "-");
  setText("aiBias", ai.ai_bias ?? "-");
  setText("aiConfidence", ai.confidence ?? "-");
  
  if (!autoRunning) {
  setText("aiPermission", ai.trade_permission ?? "-");
}
  setText("aiReason", ai.reason ?? "-");

  setText("heroAiBias", formatExecutionAction(execution, ai));
  setText("heroConfidence", formatConfidence(ai.confidence));

  if (!autoRunning) {
  setText("heroPermission", formatArgosState(ai));
  setText("aiPermission", formatArgosState(ai));
}

setText("heroRiskMode", formatRiskMode(ai.risk_mode));
setText("aiReason", execution.reason ?? ai.argos_message ?? ai.reason ?? "-");

  const strategy = (backtest.strategies || [])[0] || {};
  setText("backtestMode", backtest.mode ?? "-");
  setText("backtestStrategy", strategy.name ?? "-");
  setText("backtestTrades", strategy.total_trades ?? 0);
  setText("backtestWinRate", (strategy.win_rate ?? 0) + "%");
  setText("backtestPnl", strategy.total_pnl ?? 0);

  setText("marketUpdated", data.market?.updated_at || "-");

  setText("chartSymbol", chart.symbol ?? "BTCUSDT");
  setText("chartDirection", chart.direction ?? "WAIT");
  setText("chartEntry", chart.entry ?? 0);
  setText("chartTp", chart.tp ?? 0);
  setText("chartSl", chart.sl ?? 0);
  setText("chartCurrent", chart.current ?? 0);

  renderRadar(results);
  renderMarketTable(results);
  renderPositions(positions);
  renderHomePositions(positions);
  renderNews(news.headlines || []);
  renderMacro(macro.events || []);
  renderSymbolPerformance(analytics.symbols || {});
  renderDecisionLogs(data.decision_logs || []);
  renderSystemLogs(data.system_logs || []);
  renderTrades(data.trades || []);
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) {
    el.textContent = value;
  }
}

function formatConfidence(value) {
  if (value === undefined || value === null || value === "-") return "-";
  return value + "%";
}

function formatPermission(value) {
  if (!value) return "-";
  if (value === true) return "AUTO READY";
  if (value === false) return "MARKET BLOCKED";

  const text = String(value).toUpperCase();

  if (text === "BLOCK") return "MARKET BLOCKED";
  if (text === "WAIT") return "AI WAITING";
  if (text === "READY") return "AUTO READY";
  if (text === "ALLOW") return "AUTO READY";

  return text;
}

function formatNumber(value) {
  const num = Number(value);
  if (Number.isNaN(num)) return value;
  return num.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

function formatArgosState(ai) {
  if (!ai) return "-";

  const state = ai.argos_state || ai.trade_permission || "-";

  if (state === "BLOCKED") return "MARKET BLOCKED";
  if (state === "ANALYZING") return "AI ANALYZING";
  if (state === "READY_LONG") return "READY LONG";
  if (state === "READY_SHORT") return "READY SHORT";
  if (state === "RUNNING") return "AI RUNNING";

  return String(state).toUpperCase();
}

function formatArgosBias(ai) {
  if (!ai) return "-";

  if (ai.argos_state === "BLOCKED") return "NO TRADE";
  if (ai.argos_state === "ANALYZING") return "WAIT";
  if (ai.argos_state === "READY_LONG") return "LONG";
  if (ai.argos_state === "READY_SHORT") return "SHORT";

  return ai.ai_bias || "-";
}

function formatRiskMode(value) {
  if (!value) return "-";

  const text = String(value).toUpperCase();

  if (text === "DEFENSIVE") return "DEFENSIVE MODE";
  if (text === "NORMAL") return "NORMAL MODE";
  if (text === "AGGRESSIVE") return "AGGRESSIVE MODE";

  return text;
}

function formatExecutionAction(execution, ai) {
  if (execution && execution.paper_order_ready) {
    if (execution.direction === "LONG") return "LONG READY";
    if (execution.direction === "SHORT") return "SHORT READY";
  }

  if (ai && ai.argos_state === "BLOCKED") return "NO TRADE";
  if (ai && ai.argos_state === "ANALYZING") return "WAIT";

  return ai?.ai_bias || "-";
}

function renderRadar(results) {
  const box = document.getElementById("radarGrid");
  if (!box) return;

  box.innerHTML = "";

  results.forEach(r => {
    const item = document.createElement("div");
    item.className = "radar-item";

    item.innerHTML = `
      <div class="radar-symbol">${r.symbol}</div>
      <div class="radar-action">${r.action}</div>
      <div class="radar-score">Signal ${r.signal_score}</div>
    `;

    box.appendChild(item);
  });
}

function renderMarketTable(results) {
  const rows = document.getElementById("marketRows");
  if (!rows) return;

  rows.innerHTML = "";

  results.forEach(r => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${r.symbol}</td>
      <td>${r.price}</td>
      <td>${r.action}</td>
    `;
    rows.appendChild(row);
  });
}

function renderPositions(positions) {
  const rows = document.getElementById("positionRows");
  if (!rows) return;

  rows.innerHTML = "";

  if (positions.length === 0) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="7">NO OPEN POSITIONS</td>`;
    rows.appendChild(row);
    return;
  }

  function renderHomePositions(positions) {
  const box = document.getElementById("homePositionsList");
  if (!box) return;

  setText("homePositionCount", positions.length);

  box.innerHTML = "";

  if (positions.length === 0) {
    box.innerHTML = `
      <div class="empty-position">
        NO OPEN POSITIONS
      </div>
    `;
    return;
  }

  positions.forEach(p => {
    const card = document.createElement("div");
    card.className = "home-position-card";

    const market = p.market || "CRYPTO";
    const symbol = p.symbol || "-";
    const direction = p.direction || p.action || "-";
    const entry = p.entry ?? 0;
    const current = p.current_price ?? p.current ?? 0;
    const size = p.position_size ?? 0;
    const pnl = p.unrealized_pnl ?? p.pnl ?? 0;

    card.innerHTML = `
      <div class="home-position-head">
        <div>
          <span>${market}</span>
          <strong>${symbol}</strong>
        </div>
        <b>${direction}</b>
      </div>

      <div class="home-position-grid">
        <div><span>Entry</span><strong>${entry}</strong></div>
        <div><span>Current</span><strong>${current}</strong></div>
        <div><span>Size</span><strong>${size}</strong></div>
        <div><span>PnL</span><strong>${pnl}</strong></div>
      </div>
    `;

    box.appendChild(card);
  });
}

  positions.forEach(p => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${p.symbol}</td>
      <td>${p.action}</td>
      <td>${p.entry}</td>
      <td>${p.current_price}</td>
      <td>${p.unrealized_pnl}</td>
      <td>${p.tp_distance_pct}%</td>
      <td>${p.sl_distance_pct}%</td>
    `;
    rows.appendChild(row);
  });
}

function renderNews(headlines) {
  const rows = document.getElementById("newsRows");
  if (!rows) return;

  rows.innerHTML = "";

  headlines.slice(0, 5).forEach(h => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${h.title}</td>`;
    rows.appendChild(row);
  });
}

function renderMacro(events) {
  const rows = document.getElementById("macroRows");
  if (!rows) return;

  rows.innerHTML = "";

  events.slice(0, 5).forEach(e => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${e.title}</td>`;
    rows.appendChild(row);
  });
}

function renderSymbolPerformance(symbols) {
  const rows = document.getElementById("symbolRows");
  if (!rows) return;

  rows.innerHTML = "";

  Object.keys(symbols).forEach(symbol => {
    const s = symbols[symbol];
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${symbol}</td>
      <td>${s.total}</td>
      <td>${s.wins}</td>
      <td>${s.losses}</td>
      <td>${s.win_rate}%</td>
      <td>${s.pnl}</td>
    `;
    rows.appendChild(row);
  });
}

function renderDecisionLogs(logs) {
  const rows = document.getElementById("decisionRows");
  if (!rows) return;

  rows.innerHTML = "";

  logs.slice(-3).reverse().forEach(d => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${d.time}</td>
      <td>${d.symbol}</td>
      <td>${d.action}</td>
      <td>${d.reason}</td>
    `;
    rows.appendChild(row);
  });
}

function renderSystemLogs(logs) {
  const rows = document.getElementById("systemRows");
  if (!rows) return;

  rows.innerHTML = "";

  logs.slice(-5).reverse().forEach(s => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${s.time}</td>
      <td>${s.level}</td>
      <td>${s.module}</td>
      <td>${s.message}</td>
    `;
    rows.appendChild(row);
  });
}

function renderTrades(trades) {
  const rows = document.getElementById("trades");
  if (!rows) return;

  rows.innerHTML = "";

  trades.slice(-3).reverse().forEach(t => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${t.time}</td>
      <td>${t.symbol}</td>
      <td>${t.action}</td>
      <td>${t.entry}</td>
      <td>${t.exit}</td>
      <td>${t.pnl}</td>
      <td>${t.result}</td>
    `;
    rows.appendChild(row);
  });
}

function scrollToSection(id) {
  const target = document.getElementById(id);

  if (target) {
    target.scrollIntoView({
      behavior: "smooth",
      block: "start"
    });
  }
}

loadData();
setInterval(loadData, 3000);

function startAuto() {
  autoRunning = true;

  setText("heroPermission", "AI AUTO RUNNING");
  setText("aiPermission", "AI AUTO RUNNING");
}

function stopAuto() {
  autoRunning = false;

  setText("heroPermission", "AUTO STOPPED");
  setText("aiPermission", "AUTO STOPPED");
}

function showTab(tabName) {

  document.querySelectorAll(".tab-page")
    .forEach(page => {
      page.classList.remove("active-page");
    });

  document.querySelectorAll(".tab")
    .forEach(tab => {
      tab.classList.remove("active");
    });

  document
    .getElementById("tab-" + tabName)
    .classList.add("active-page");

  event.target.classList.add("active");
}

function loadChart() {

  const symbol =
    document.getElementById("chartSearch").value ||
    "BTCUSDT";

  document.getElementById("chartSymbol").textContent = symbol;
}