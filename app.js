const PROFILE_FACTORS = {
  "Rectangle – Constant Cross Section": 0.67
};

const profileSelect = document.getElementById("profile");
Object.keys(PROFILE_FACTORS).forEach(p => {
  const opt = document.createElement("option");
  opt.value = p;
  opt.textContent = p;
  profileSelect.appendChild(opt);
});

function calculateSnapFit(profile, E, eps, L, h, b, mu, alphaDeg) {
  const alpha = alphaDeg * Math.PI / 180;
  const factor = PROFILE_FACTORS[profile];

  const y = factor * eps * L * L / h;
  const Z = b * h * h / 6;

  const P = Z * E * eps / L;
  const W = P * ((mu + Math.tan(alpha)) / (1 - mu * Math.tan(alpha)));

  return { y, P, W };
}

function runCalculation() {
  const profile = profileSelect.value;
  const E = +document.getElementById("E").value;
  const eps = +document.getElementById("eps").value;
  const mu = +document.getElementById("mu").value;
  const alpha = +document.getElementById("alpha").value;
  const L = +document.getElementById("L").value;
  const h = +document.getElementById("h").value;
  const b = +document.getElementById("b").value;

  const res = calculateSnapFit(profile, E, eps, L, h, b, mu, alpha);

  document.getElementById("results").innerHTML = `
    <strong>Permissible Deflection y:</strong> ${res.y.toFixed(4)} in<br>
    <strong>Deflection Force P:</strong> ${res.P.toFixed(2)} lbf<br>
    <strong>Mating Force W:</strong> ${res.W.toFixed(2)} lbf
  `;

  updateChart(E, eps, mu, alpha, L, b);
}
