import streamlit as st
import numpy as np
from scipy.stats import norm

# --- Page Config ---
st.set_page_config(
    page_title="Black-Scholes Option Sketch",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Georgia', serif;
            background-color: #f8f5f0;
            color: #1e1e1e;
        }
        h1, h2, h3 {
            font-family: 'Georgia', serif;
            font-weight: 500;
        }
        .stButton button {
            background-color: #ccc;
            color: #000;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("📈 Black-Scholes Option Sketch")

st.markdown("""
A minimal calculator for European call and put options using the classical Black-Scholes-Merton framework.
""")

# --- Sidebar: Parameters ---
st.sidebar.header("✒️ Option Parameters")
S = st.sidebar.number_input("Spot Price (S₀)", value=100.0, step=1.0)
K = st.sidebar.number_input("Strike Price (K)", value=100.0, step=1.0)
T = st.sidebar.number_input("Time to Maturity (T)", value=1.0, step=0.1)
r = st.sidebar.number_input("Risk-Free Rate (r)", value=0.01, step=0.001)
sigma = st.sidebar.number_input("Volatility (σ)", value=0.2, step=0.01)

# --- Pricing Function ---
def black_scholes_price(S, K, T, r, sigma, option_type="call"):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2), d1, d2
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1), d1, d2

# --- Compute Prices ---
call_price, d1, d2 = black_scholes_price(S, K, T, r, sigma, "call")
put_price, _, _   = black_scholes_price(S, K, T, r, sigma, "put")

# --- Results Display ---
st.subheader("🎯 Results")
st.markdown(f"""
- **Call Option Price**: ${call_price:.4f}  
- **Put Option Price**: ${put_price:.4f}  
""")

st.subheader("🧠 Mathematical Details")
st.latex(r"""
d_1 = \frac{\ln(\frac{S_0}{K}) + (r + \frac{1}{2} \sigma^2) T}{\sigma \sqrt{T}}, \quad
d_2 = d_1 - \sigma \sqrt{T}
""")
st.markdown(f"d₁ = `{d1:.4f}`  d₂ = `{d2:.4f}`")
