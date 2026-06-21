async function loadData() {
  const res = await fetch("/api/status");
  const data = await res.json();

  document.getElementById("total").textContent = data.report.total_trades;
  document.getElementById("wins").textContent = data.report.wins;
  document.getElementById("losses").textContent = data.report.losses;
  document.getElementById("winRate").textContent = data.report.win_rate + "%";
  document.getElementById("pnl").textContent = data.report.total_pnl;

  const tbody = document.getElementById("trades");
  tbody.innerHTML = "";

  data.trades.slice(-10).reverse().forEach(t => {
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