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
  const paperRouter = data.paper_router || {};
  const chart = data.chart || {};
  const brain = data.brain || {};
  const homeSummary = data.home_summary || {};
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

  setText("heroAiBias", homeSummary.ai_state ?? formatBrainDecision(brain, execution, ai));
  setText("heroConfidence", formatConfidence(homeSummary.ai_confidence ?? brain.ai_summary?.confidence ?? ai.confidence));
  setText("heroMarket", homeSummary.market ?? "CRYPTO");
  setText("heroSymbol", homeSummary.symbol ?? "-");
  setText("heroDecision", homeSummary.decision ?? "-");
  setText("heroExecution", homeSummary.execution ?? "NO_ORDER");
  setText("heroRouterReason", homeSummary.router_reason ?? "-");
  setText("heroAiReason", homeSummary.ai_reason ?? "-");
  setText("heroRiskMode", formatRiskMode(homeSummary.risk_mode ?? ai.risk_mode));
  
  if (!autoRunning) {
  setText("heroPermission", formatArgosState(ai));
  setText("settingsPermission", formatArgosState(ai));
  setText("aiPermission", formatArgosState(ai));
}

setText("settingsRiskMode", formatRiskMode(ai.risk_mode));
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
  renderTradingView(chart);
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

async function loadChart() {
  const symbol =
    document.getElementById("chartSearch").value ||
    "BTCUSDT";

  const market =
    document.getElementById("chartMarket").value ||
    "CRYPTO";

  const res = await fetch(
    `/api/chart?market=${encodeURIComponent(market)}&symbol=${encodeURIComponent(symbol)}`
  );

  const chart = await res.json();

  setText("chartSymbol", chart.symbol ?? symbol);
  setText("chartDirection", chart.direction ?? "WAIT");
  setText("chartEntry", chart.entry ?? 0);
  setText("chartTp", chart.tp ?? 0);
  setText("chartSl", chart.sl ?? 0);
  setText("chartCurrent", chart.current ?? 0);

  renderTradingView(chart);
}

function formatBrainDecision(brain, execution, ai) {
  const decision = brain.decision_summary?.decision;
  const action = brain.decision_summary?.action;

  if (decision === "BLOCK") return "NO TRADE";
  if (action === "PAPER_LONG") return "LONG";
  if (action === "PAPER_SHORT") return "SHORT";
  if (decision === "WAIT") return "WAIT";

  return formatExecutionAction(execution, ai);
}

function renderTradingView(chart) {
  const box = document.getElementById("tradingviewChart");
  if (!box) return;

  const symbol = chart.display_symbol || "BINANCE:BTCUSDT";

  box.innerHTML = "";

  const widgetBox = document.createElement("div");
  widgetBox.className = "tradingview-widget-container";
  widgetBox.style.height = "100%";
  widgetBox.style.width = "100%";

  const chartDiv = document.createElement("div");
  chartDiv.className = "tradingview-widget-container__widget";
  chartDiv.style.height = "100%";
  chartDiv.style.width = "100%";

  const script = document.createElement("script");
  script.type = "text/javascript";
  script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
  script.async = true;

  script.innerHTML = JSON.stringify({
    autosize: true,
    symbol: symbol,
    interval: "5",
    timezone: "Asia/Seoul",
    theme: "dark",
    style: "1",
    locale: "en",
    allow_symbol_change: true,
    calendar: false,
    support_host: "https://www.tradingview.com"
  });

  widgetBox.appendChild(chartDiv);
  widgetBox.appendChild(script);
  box.appendChild(widgetBox);
}