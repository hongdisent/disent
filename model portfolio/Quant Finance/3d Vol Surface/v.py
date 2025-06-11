import streamlit as st
import numpy as np
from scipy.stats import norm
from scipy.interpolate import griddata
from concurrent.futures import ThreadPoolExecutor
import plotly.graph_objects as go
import yfinance as yf
import datetime
import pandas as pd

# ─────────────────────────────
# 🚀 PROJECT INTRODUCTION
# ─────────────────────────────
st.set_page_config(page_title="3D Implied Volatility Surface", layout="centered")
st.title("📈 3D Implied Volatility Surface Modeling")

st.markdown("""
This app calculates and visualizes **implied volatility surfaces** for options using market data from Yahoo Finance.

- We use the **Black-Scholes model** and Newton-Raphson method to estimate implied volatilities.
- Volatility is plotted across **strike prices** and **days to expiry** using a 3D surface.
- Select **calls or puts**, and control the risk-free rate and expiration depth via the sidebar.

This tool is ideal for quant researchers, traders, and educators exploring volatility term structure and smile effects.
""")

# ─────────────────────────────
# 📥 SIDEBAR INPUTS
# ─────────────────────────────
ticker = st.sidebar.text_input("Stock Ticker", value="AAPL").upper()
option_type = st.sidebar.selectbox("Option Type", ["Calls", "Puts"])
r = st.sidebar.number_input("Risk-Free Rate", min_value=0.0, max_value=0.1, value=0.02, step=0.005)
exp_date_limit = st.sidebar.slider("Number of Expirations", 1, 10, 4)

# ─────────────────────────────
# 🧠 IV Calculation Functions
# ─────────────────────────────
def black_scholes_price(S, K, T, r, sigma, q=0.0, is_call=True):
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if is_call:
        return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)

def implied_vol(market_price, S, K, T, r, is_call=True, max_iter=100, tol=1e-4):
    sigma = 0.3
    for _ in range(max_iter):
        price = black_scholes_price(S, K, T, r, sigma, is_call=is_call)
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T)
        if vega == 0: return None
        diff = price - market_price
        if abs(diff) < tol: return sigma
        sigma -= diff / vega
    return None

# ─────────────────────────────
# 📦 Load Option Data
# ─────────────────────────────
try:
    stock = yf.Ticker(ticker)
    S0 = stock.history(period="1d")['Close'].iloc[-1]
    expirations = stock.options[:exp_date_limit]
except Exception as e:
    st.error(f"Failed to load data for {ticker}: {e}")
    st.stop()

all_points = []

def process_chain(row, T, opt_type):
    K = row['strike']
    price = row['lastPrice'] if row['lastPrice'] > 0 else (row['bid'] + row['ask']) / 2
    if price <= 0: return None
    iv = implied_vol(price, S0, K, T / 365, r, is_call=(opt_type == "Call"))
    if iv is not None and 0.01 < iv < 3.0:
        return (K, T, iv)

# ─────────────────────────────
# 🔁 Loop over Expirations
# ─────────────────────────────
for expiry in expirations:
    try:
        option_chain = stock.option_chain(expiry)
        expiry_dt = datetime.datetime.strptime(expiry, "%Y-%m-%d")
        T = (expiry_dt - datetime.datetime.now()).days
        if T <= 0: continue

        with ThreadPoolExecutor() as executor:
            options_df = option_chain.calls if option_type == "Calls" else option_chain.puts
            results = executor.map(lambda row: process_chain(row, T, option_type[:-1]), [row for _, row in options_df.iterrows()])
            all_points += [res for res in results if res]
    except:
        continue

if not all_points:
    st.warning("No valid IV data found.")
    st.stop()

# ─────────────────────────────
# 📊 Build Surface Plot
# ─────────────────────────────
df = pd.DataFrame(all_points, columns=['strike', 'dte', 'iv'])
K_vals = np.linspace(df['strike'].min(), df['strike'].max(), 40)
T_vals = np.linspace(df['dte'].min(), df['dte'].max(), 40)
K_mesh, T_mesh = np.meshgrid(K_vals, T_vals)
IV_grid = griddata(df[['strike', 'dte']].values, df['iv'].values, (K_mesh, T_mesh), method='linear')

fig = go.Figure(data=[go.Surface(
    x=K_vals,
    y=T_vals,
    z=IV_grid,
    colorscale='Viridis',
    colorbar=dict(title="Implied Volatility"),
    opacity=0.9
)])

fig.update_layout(
    title=f"{ticker} Implied Volatility Surface ({option_type})",
    scene=dict(
        xaxis_title='Strike Price (K)',
        yaxis_title='Days to Expiry (T)',
        zaxis_title='Implied Volatility (σ)'
    ),
    width=1000,
    height=700
)

st.plotly_chart(fig, use_container_width=True)
