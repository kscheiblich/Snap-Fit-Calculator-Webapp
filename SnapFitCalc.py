import streamlit as st
from streamlit.components.v1 import html
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ======================================================
# PAGE CONFIG + CENTERING STYLE
# ======================================================

st.set_page_config(
    page_title="Plastic Snap-Fit Design Calculator",
    layout="wide"
)

#----------------GOOGLE ANALYTICS-----------------------
html("""
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-HN1G7V18X9"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-HN1G7V18X9');
</script>
""", height = 0, width = 0)

st.markdown(
    """
    <style>
    h1, h2, h3, h4 { text-align: center; }
    div[data-baseweb="tab-list"] { justify-content: center; }
    .calculator-output { text-align: center; margin-bottom: 10px; }
    .assumptions { text-align: center; }
    </style>
    """,
    unsafe_allow_html=True
)

# ======================================================
# UNIT SELECTION
# ======================================================

unit_system = st.radio("Select Unit System", ["Imperial", "Metric"], index=0)
length_unit = "in" if unit_system == "Imperial" else "mm"
E_unit = "psi" if unit_system == "Imperial" else "Pa"
force_unit = "lbf" if unit_system == "Imperial" else "N"

# ======================================================
# CONVERSIONS
# ======================================================

def in_to_mm(val): return val * 25.4
def mm_to_in(val): return val / 25.4
def lbf_to_N(val): return val * 4.44822
def N_to_lbf(val): return val / 4.44822
def psi_to_Pa(val): return val * 6894.76
def Pa_to_psi(val): return val / 6894.76

# ======================================================
# GEOMETRY FACTORS
# ======================================================

PROFILE_FACTORS = {
    "Rectangle – Constant Cross Section": 0.67,
    "Rectangle – Y Dimensions Halved": 1.09,
    "Rectangle – Z Dimensions Quartered": 0.86,
    "Trapezoid – Constant Cross Section": 1.00,
    "Trapezoid – Y Dimensions Halved": 1.64,
    "Trapezoid – Z Dimensions Quartered": 1.28,
    "Ring Segment – Constant Cross Section": 1.00,
    "Ring Segment – Y Dimensions Halved": 1.64,
    "Ring Segment – Z Dimensions Quartered": 1.28,
    "Irregular – Constant Cross Section": 1/3,
    "Irregular – Y Dimensions Halved": 0.55,
    "Irregular – Z Dimensions Quartered": 0.43
}

# ======================================================
# CALCULATION ENGINE
# ======================================================

def calculate_snap_fit(profile, E, eps, L, h=None, b=None, a=None, r2=None, Z=None, mu=0.3, alpha_deg=5):
    alpha = np.radians(alpha_deg)
    factor = PROFILE_FACTORS[profile]

    if "Rectangle" in profile:
        y = factor * eps * L**2 / h
        Z_sec = b * h**2 / 6
    elif "Trapezoid" in profile:
        y = factor * ((a + b) / (2*a + b)) * eps * L**2 / h
        Z_sec = (h**2 / 12) * ((a**2 + 4*a*b + b**2) / (2*a + b))
    elif "Ring Segment" in profile:
        y = factor * eps * L**2 / r2
        Z_sec = Z
    else:  # Irregular
        y = factor * eps * L**2 / h
        Z_sec = Z

    P = Z_sec * E * eps / L
    W = P * ((mu + np.tan(alpha)) / (1 - mu * np.tan(alpha)))

    return {"Permissible Deflection (y)": y, "Deflection Force (P)": P, "Mating Force (W)": W}

# ======================================================
# DEFAULT INPUTS
# ======================================================

def default_inputs():
    if unit_system == "Imperial":
        return {"L":1.0, "h":0.10, "b":0.50, "a":0.60, "r2":0.50, "Z":0.01, "E":300_000.0}
    else:
        return {"L":25.4, "h":2.54, "b":12.7, "a":15.24, "r2":12.7, "Z":4.14e-7, "E":2.07e9}

defaults = default_inputs()

# ======================================================
# HEADER
# ======================================================

st.title("Plastic Snap-Fit Design Calculator")
st.markdown("<p style='text-align:center;'>Analytical snap-fit sizing tool based on Bayer Snap Fit Design for Plastics</p>", unsafe_allow_html=True)
st.divider()

# ======================================================
# TABS
# ======================================================

tab_calc, tab_param, tab_eq, tab_assump = st.tabs(
    ["📐 Calculator", "📊 Parametric Study", "📘 Equations", "⚠️ Assumptions, Limits, and References"]
)

# ======================================================
# CALCULATOR TAB
# ======================================================

with tab_calc:
    col_in, col_out = st.columns([1.2, 0.8])

    with col_in:
        st.subheader("Inputs")
        profile = st.selectbox("Geometric Profile", list(PROFILE_FACTORS.keys()))
        st.markdown("**Material**")
        E = st.number_input(f"Elastic Modulus [{E_unit}]", value=defaults["E"])
        eps = st.number_input("Allowable Strain ε [-]", value=0.02)
        st.markdown("**Contact**")
        mu = st.number_input("Coefficient of Friction μ [-]", value=0.30)
        alpha = st.number_input("Lead-in Angle α (deg)", value=5.0)
        st.divider()
        st.markdown("**Geometry**")
        L = st.number_input(f"Cantilever Length [{length_unit}]", value=defaults["L"])
        h = b = a = r2 = Z = None

        if "Rectangle" in profile:
            h = st.number_input(f"Thickness h [{length_unit}]", value=defaults["h"])
            b = st.number_input(f"Width b [{length_unit}]", value=defaults["b"])
        elif "Trapezoid" in profile:
            h = st.number_input(f"Root Thickness h [{length_unit}]", value=defaults["h"])
            a = st.number_input(f"Root Width a [{length_unit}]", value=defaults["a"])
            b = st.number_input(f"Tip Width b [{length_unit}]", value=defaults["b"])
        elif "Ring Segment" in profile:
            r2 = st.number_input(f"Outer Radius r₂ [{length_unit}]", value=defaults["r2"])
            Z = st.number_input(f"Section Modulus Z [{'in³' if unit_system == 'Imperial' else 'm³'}]", value=defaults["Z"])
        else:
            h = st.number_input(f"Effective Thickness h [{length_unit}]", value=defaults["h"])
            Z = st.number_input(f"Section Modulus Z [{'in³' if unit_system == 'Imperial' else 'm³'}]", value=defaults["Z"])

        results = calculate_snap_fit(profile, E, eps, L, h=h, b=b, a=a, r2=r2, Z=Z, mu=mu, alpha_deg=alpha)

        if unit_system == "Metric":
            results["Permissible Deflection (y)"] *= 25.4
            results["Deflection Force (P)"] *= 4.44822
            results["Mating Force (W)"] *= 4.44822

    with col_out:
        st.subheader("Outputs")
        for k, v in results.items():
            unit_label = force_unit if "Force" in k else length_unit if "Deflection" in k else ""
            st.markdown(f"<div class='calculator-output'><strong>{k}:</strong><br>{v:.4f} {unit_label}</div>", unsafe_allow_html=True)

# ======================================================
# PARAMETRIC STUDY TAB
# ======================================================

# Global storage for parametric data
if 'param_df' not in st.session_state:
    st.session_state['param_df'] = None

with tab_param:
    st.subheader("Parametric Study")
    st.markdown("<p style='text-align:center;'>Single-parameter sensitivity exploration</p>", unsafe_allow_html=True)
    st.divider()

    col_inputs, col_chart = st.columns([1,1])

    with col_inputs:
        sweep_param = st.selectbox("Parameter to Sweep", ["Thickness h", "Length L", "Allowable Strain ε"])
        start_default = defaults["h"] if sweep_param=="Thickness h" else defaults["L"] if sweep_param=="Length L" else 0.01
        stop_default = defaults["h"]*3 if sweep_param=="Thickness h" else defaults["L"]*3 if sweep_param=="Length L" else 0.05
        start = st.number_input(f"Start [{length_unit if 'h' in sweep_param or 'L' in sweep_param else ''}]", value=start_default)
        stop = st.number_input(f"Stop [{length_unit if 'h' in sweep_param or 'L' in sweep_param else ''}]", value=stop_default)
        steps = st.slider("Steps", 5, 50, 20)

    vals = np.linspace(start, stop, steps)
    rows = []

    for v in vals:
        h_s, L_s, eps_s = defaults["h"], defaults["L"], 0.02
        if sweep_param=="Thickness h": h_s=v
        elif sweep_param=="Length L": L_s=v
        else: eps_s=v

        res = calculate_snap_fit("Rectangle – Constant Cross Section", defaults["E"], eps_s, L_s, h=h_s, b=defaults["b"], mu=mu, alpha_deg=alpha)
        rows.append({"Sweep Value": v, **res})

    df = pd.DataFrame(rows)

    # Store df in session state for dynamic unit switching
    st.session_state['param_df'] = df.copy()

    # Apply unit conversion dynamically
    df_plot = df.copy()
    if unit_system=="Metric":
        if sweep_param != "Allowable Strain ε":
            df_plot["Sweep Value"] = df_plot["Sweep Value"] * 25.4
        df_plot["Deflection Force (P)"] *= 4.44822
        df_plot["Mating Force (W)"] *= 4.44822
        df_plot["Permissible Deflection (y)"] *= 25.4
    else:
        if sweep_param != "Allowable Strain ε":
            df_plot["Sweep Value"] = df_plot["Sweep Value"] / 25.4
        df_plot["Deflection Force (P)"] = df_plot["Deflection Force (P)"].apply(N_to_lbf)
        df_plot["Mating Force (W)"] = df_plot["Mating Force (W)"].apply(N_to_lbf)
        df_plot["Permissible Deflection (y)"] = df_plot["Permissible Deflection (y)"].apply(mm_to_in)

    with col_chart:
        fig, ax = plt.subplots(figsize=(5,3))
        ax.plot(df_plot["Sweep Value"], df_plot["Deflection Force (P)"], label="Deflection Force P")
        ax.plot(df_plot["Sweep Value"], df_plot["Mating Force (W)"], label="Mating Force W")
        ax.set_xlabel(f"{sweep_param} [{length_unit if 'h' in sweep_param or 'L' in sweep_param else ''}]")
        ax.set_ylabel(f"Force [{force_unit}]")
        ax.set_title("Parametric Study: Forces vs Sweep Value")
        ax.legend()
        st.pyplot(fig)
        st.dataframe(df_plot, use_container_width=True)

# ======================================================
# EQUATIONS TAB
# ======================================================

with tab_eq:
    st.subheader("Governing Equations")
    st.markdown("<p style='text-align:center;'>Per selected geometry</p>", unsafe_allow_html=True)
    st.divider()
    st.latex(r"y = C \cdot \frac{\varepsilon L^2}{h}")
    st.latex(r"P = Z \cdot \frac{E \varepsilon}{L}")
    st.latex(r"W = P \cdot \frac{\mu + \tan(\alpha)}{1 - \mu \tan(\alpha)}")

# ======================================================
# ASSUMPTIONS TAB
# ======================================================

with tab_assump:
    st.subheader("Assumptions, Limits, & References")
    st.markdown(
        "<div class='assumptions'>"
        "- Linear elastic material behavior<br>"
        "- Small deflection beam theory<br>"
        "- No creep, fatigue, or stress relaxation<br>"
        "- Idealized geometry (no fillets, draft, or tolerances)<br>"
        "- Constant friction coefficient<br>"
        "- Recommended <strong>L/h ≥ 5</strong><br>"
        "- Not valid for viscoelastic polymers without correction<br><br>"
        "<strong>Use for concept design only. Validate with FEA and testing.</strong><br><br>"
        "Reference: <a href='https://fab.cba.mit.edu/classes/S62.12/people/vernelle.noel/Plastic_Snap_fit_design.pdf' target='_blank'>Plastic Snap-Fit Design (MIT)</a>"
        "</div>",
        unsafe_allow_html=True
    )
