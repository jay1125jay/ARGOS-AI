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
  const positionsData = data.positions || { positions: [] };
  const positions = positionsData.positions || [];
  const health = data.health || {};

  document.getElementById("startBalance").textContent = portfolio.start_balance ?? 0;
  document.getElementById("currentBalance").textContent = portfolio.current_balance ?? 0;
  document.getElementById("totalReturn").textContent = (portfolio.total_return_pct ?? 0) + "%";
  document.getElementById("openPositions").textContent = positions.length;

  document.getElementById("healthStatus").textContent = health.status ?? "-";
  document.getElementById("healthFilesOk").textContent = health.files_ok ?? 0;
  document.getElementById("healthFilesTotal").textContent = health.files_total ?? 0;

  document.getElementById("total").textContent = report.total_trades ?? 0;
  document.getElementById("wins").textContent = report.wins ?? 0;
  document.getElementById("losses").textContent = report.losses ?? 0;
  document.getElementById("winRate").textContent = (report.win_rate ?? 0) + "%";
  document.getElementById("pnl").textContent = report.total_pnl ?? 0;

  document.getElementById("profitFactor").textContent = analytics.profit_factor ?? 0;
  document.getElementById("avgWin").textContent = analytics.avg_win ?? 0;
  document.getElementById("avgLoss").textContent = analytics.avg_loss ?? 0;

  document.getElementById("newsMode").textContent = news.mode ?? "-";
  document.getElementById("newsSentiment").textContent = news.market_sentiment ?? "-";
  document.getElementById("newsRisk").textContent = news.risk_level ?? "-";

  const newsRows = document.getElementById("newsRows");
  newsRows.innerHTML = "";

  (news.headlines || []).slice(0, 10).forEach(h => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${h.title}</td>
    `;
    newsRows.appendChild(row);
  });

  document.getElementById("macroMode").textContent = macro.mode ?? "-";
  document.getElementById("macroRegime").textContent = macro.market_regime ?? "-";
  document.getElementById("macroDxy").textContent = macro.dxy_status ?? "-";
  document.getElementById("macroRate").textContent = macro.rate_risk ?? "-";

  const macroRows = document.getElementById("macroRows");
  macroRows.innerHTML = "";

  (macro.events || []).slice(0, 10).forEach(e => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${e.title}</td>
    `;
    macroRows.appendChild(row);
  });
  
  document.getElementById("aiMode").textContent = ai.mode ?? "-";
  document.getElementById("aiBias").textContent = ai.ai_bias ?? "-";
  document.getElementById("aiConfidence").textContent = ai.confidence ?? "-";
  document.getElementById("aiPermission").textContent = ai.trade_permission ?? "-";
  document.getElementById("aiReason").textContent = ai.reason ?? "-";

  document.getElementById("heroAiBias").textContent = ai.ai_bias ?? "-";
  document.getElementById("heroConfidence").textContent = ai.confidence ?? "-";
  document.getElementById("heroPermission").textContent = ai.trade_permission ?? "-";
  document.getElementById("heroRiskMode").textContent = ai.risk_mode ?? "-";

  const strategy = (backtest.strategies || [])[0] || {};

  document.getElementById("backtestMode").textContent = backtest.mode ?? "-";
  document.getElementById("backtestStrategy").textContent = strategy.name ?? "-";
  document.getElementById("backtestTrades").textContent = strategy.total_trades ?? 0;
  document.getElementById("backtestWinRate").textContent = (strategy.win_rate ?? 0) + "%";
  document.getElementById("backtestPnl").textContent = strategy.total_pnl ?? 0;

  const positionRows = document.getElementById("positionRows");
  positionRows.innerHTML = "";

  if (positions.length === 0) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td colspan="9">NO OPEN POSITIONS</td>
    `;
    positionRows.appendChild(row);
  } else {
    positions.forEach(p => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${p.symbol}</td>
        <td>${p.action}</td>
        <td>${p.entry}</td>
        <td>${p.tp}</td>
        <td>${p.sl}</td>
        <td>${p.current_price}</td>
        <td>${p.unrealized_pnl}</td>
        <td>${p.tp_distance_pct}%</td>
        <td>${p.sl_distance_pct}%</td>
      `;
      positionRows.appendChild(row);
    });
  }

  document.getElementById("marketUpdated").textContent = data.market?.updated_at || "-";

  const marketRows = document.getElementById("marketRows");
  marketRows.innerHTML = "";

  const results = data.market?.results || [];

  results.forEach(r => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${r.symbol}</td>
      <td>${r.price}</td>
      <td>${r.change_pct}</td>
      <td>${r.rsi}</td>
      <td>${r.ema9 ?? "-"}</td>
      <td>${r.ema21 ?? "-"}</td>
      <td>${r.trend ?? "-"}</td>
      <td>${r.volume_ratio ?? "-"}</td>
      <td>${r.atr_pct ?? "-"}</td>
      <td>${r.signal_score}</td>
      <td>${r.risk_score}</td>
      <td>${r.action}</td>
    `;
    marketRows.appendChild(row);
  });

    const symbolRows = document.getElementById("symbolRows");
  symbolRows.innerHTML = "";

  const symbols = analytics.symbols || {};

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
    symbolRows.appendChild(row);
  });

  const decisionRows = document.getElementById("decisionRows");
  decisionRows.innerHTML = "";

  (data.decision_logs || []).slice(-10).reverse().forEach(d => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${d.time}</td>
      <td>${d.symbol}</td>
      <td>${d.action}</td>
      <td>${d.signal_score}</td>
      <td>${d.risk_score}</td>
      <td>${d.reason}</td>
      <td>${d.strategy_version}</td>
    `;
    decisionRows.appendChild(row);
  });

  const systemRows = document.getElementById("systemRows");
  systemRows.innerHTML = "";

  (data.system_logs || []).slice(-10).reverse().forEach(s => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${s.time}</td>
      <td>${s.level}</td>
      <td>${s.module}</td>
      <td>${s.message}</td>
    `;
    systemRows.appendChild(row);
  });

  const tbody = document.getElementById("trades");
  tbody.innerHTML = "";

  (data.trades || []).slice(-10).reverse().forEach(t => {
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
    tbody.appendChild(row);
  });
}

loadData();
setInterval(loadData, 3000);
