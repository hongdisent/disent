import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Your SVI function for a single maturity
def svi(k, params):
    a, b, rho, m, sigma = params
    return a + b * (rho * (k - m) + np.sqrt((k - m)**2 + sigma**2))

# Calculate time to expiry in years
def time_to_expiry(expiry_date, current_date=datetime.today()):
    delta = expiry_date - current_date
    return max(delta.days / 365.0, 0)

# Calculate log-moneyness
def log_moneyness(strike, forward_price):
    return np.log(strike / forward_price)

# Fetch SPY option data and prepare for plotting
def fetch_spy_options_data(ticker):
    spy = yf.Ticker(ticker)
    expirations = spy.options

    data = []
    spot_price = spy.history(period="1d")['Close'].iloc[-1]
    forward_price = spot_price  # Simplified forward price, can be improved

    for expiry_str in expirations:
        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
        T = time_to_expiry(expiry_date)
        if T <= 0:
            continue

        opt_chain = spy.option_chain(expiry_str)
        calls = opt_chain.calls

        # Filter OTM calls (strike > spot)
        calls_otm = calls[calls['strike'] > spot_price]

        for _, row in calls_otm.iterrows():
            strike = row['strike']
            market_iv = row['impliedVolatility']
            k = log_moneyness(strike, forward_price)

            data.append({
                'expiry': expiry_date,
                'T': T,
                'strike': strike,
                'log_moneyness': k,
                'market_iv': market_iv
            })

    return pd.DataFrame(data)

# Main Streamlit app
def main():
    st.title("Option Implied Volatility Surface with SVI Model")

    st.markdown("""
    This app fetches real SPY option data, computes log-moneyness and time to expiry,
    applies a sample SVI model, and plots a 3D implied volatility surface.
    """)

    # Fetch and prepare data
    ticker = st.text_input("Enter Ticker Symbol", "SPY")
    df = fetch_spy_options_data(ticker)
    if df.empty:
        st.warning("No option data available.")
        return

    # User input for SVI parameters
    st.sidebar.header("SVI Parameters (example values)")
    a = st.sidebar.slider("a (base level)", 0.0, 0.1, 0.01, 0.001)
    b = st.sidebar.slider("b (skew modulation)", 0.0, 0.5, 0.1, 0.001)
    rho = st.sidebar.slider("rho (skewness)", -1.0, 1.0, -0.5, 0.01)
    m = st.sidebar.slider("m (peak location)", -0.1, 0.1, 0.07, 0.001)
    sigma = st.sidebar.slider("sigma (convexity)", 0.01, 1.0, 0.1, 0.01)

    params = (a, b, rho, m, sigma)

    # Calculate model implied variance and volatility
    df['total_variance'] = df['log_moneyness'].apply(lambda k: svi(k, params))
    df['model_iv'] = np.sqrt(df['total_variance'] / df['T'])

    # Prepare grid for surface plot
    # Create pivot table with maturities and log-moneyness
    pivot = df.pivot_table(index='T', columns='log_moneyness', values='model_iv')

    # Sort axes
    T_values = np.array(sorted(pivot.index))
    k_values = np.array(sorted(pivot.columns))
    # T_values = df['T']
    # k_values = df['log_moneyness']
    # Create meshgrid
    K, T = np.meshgrid(k_values, T_values)
    impli_vol = np.sqrt(np.array([[svi(k,params)/t for k in k_values] for t in T_values]))
    st.write(K.shape, T.shape, impli_vol.shape)
    Z = pivot.values

    # Plotly 3D surface plot
    fig = go.Figure(data=[go.Surface(x=K, y=T, z=impli_vol, colorscale='Jet')])
    fig.update_layout(
        scene=dict(
            xaxis_title='Log-Moneyness (k)',
            yaxis_title='Time to Expiry (Years)',
            zaxis_title='Implied Volatility',
        ),
        title='SVI Implied Volatility Surface for SPY Options',
        autosize=True,
        height=700,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Show raw data if user wants
    if st.checkbox("Show raw option data"):
        st.dataframe(df)

if __name__ == "__main__":
    main()
