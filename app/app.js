async function loadData() {
  const res = await fetch("/api/status");
  const data = await res.json();

  const portfolio = data.portfolio || {};
  const report = data.report || {};
  const analytics = data.analytics || {};
  const positionsData = data.positions || { positions: [] };
  const positions = positionsData.positions || [];

  document.getElementById("startBalance").textContent = portfolio.start_balance ?? 0;
  document.getElementById("currentBalance").textContent = portfolio.current_balance ?? 0;
  document.getElementById("totalReturn").textContent = (portfolio.total_return_pct ?? 0) + "%";
  document.getElementById("openPositions").textContent = positions.length;

  const position = positions[0];

  if (position) {
    document.getElementById("posSymbol").textContent = position.symbol;
    document.getElementById("posAction").textContent = position.action;
    document.getElementById("posEntry").textContent = position.entry;
    document.getElementById("posTp").textContent = position.tp;
    document.getElementById("posSl").textContent = position.sl;
    document.getElementById("posCurrent").textContent = position.current_price;
    document.getElementById("posPnl").textContent = position.unrealized_pnl;
    document.getElementById("posTpDist").textContent = position.tp_distance_pct + "%";
    document.getElementById("posSlDist").textContent = position.sl_distance_pct + "%";
  } else {
    document.getElementById("posSymbol").textContent = "NONE";
    document.getElementById("posAction").textContent = "-";
    document.getElementById("posEntry").textContent = "-";
    document.getElementById("posTp").textContent = "-";
    document.getElementById("posSl").textContent = "-";
    document.getElementById("posCurrent").textContent = "-";
    document.getElementById("posPnl").textContent = "-";
    document.getElementById("posTpDist").textContent = "-";
    document.getElementById("posSlDist").textContent = "-";
  }

  document.getElementById("total").textContent = report.total_trades ?? 0;
  document.getElementById("wins").textContent = report.wins ?? 0;
  document.getElementById("losses").textContent = report.losses ?? 0;
  document.getElementById("winRate").textContent = (report.win_rate ?? 0) + "%";
  document.getElementById("pnl").textContent = report.total_pnl ?? 0;

  document.getElementById("profitFactor").textContent = analytics.profit_factor ?? 0;
  document.getElementById("longWinRate").textContent = (analytics.long_win_rate ?? 0) + "%";
  document.getElementById("shortWinRate").textContent = (analytics.short_win_rate ?? 0) + "%";
  document.getElementById("avgWin").textContent = analytics.avg_win ?? 0;
  document.getElementById("avgLoss").textContent = analytics.avg_loss ?? 0;

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