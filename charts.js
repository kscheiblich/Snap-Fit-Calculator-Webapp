let chart;

function updateChart(E, eps, mu, alpha, L, b) {
  const hVals = [];
  const Pvals = [];
  const Wvals = [];

  for (let h = 0.05; h <= 0.30; h += 0.01) {
    const { P, W } = calculateSnapFit(
      "Rectangle – Constant Cross Section",
      E, eps, L, h, b, mu, alpha
    );
    hVals.push(h.toFixed(2));
    Pvals.push(P);
    Wvals.push(W);
  }

  if (chart) chart.destroy();

  chart = new Chart(document.getElementById("chart"), {
    type: "line",
    data: {
      labels: hVals,
      datasets: [
        { label: "Deflection Force P (lbf)", data: Pvals },
        { label: "Mating Force W (lbf)", data: Wvals }
      ]
    }
  });
}
