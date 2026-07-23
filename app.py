import streamlit as st
from datetime import date, timedelta
import yfinance as yf
from black_scholes import option_pricer
from greeks import *


#FONT AND SIDEBAR ELEMENTS AND THEME
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

.stApp {
    font-family: 'Inter', sans-serif;
}

.stApp * {
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stSidebarCollapseButton"] {
    display: none;
}
            
.metric-card {
    padding:18px;
    border-radius:18px;
    background:#141D2E;
    border:1px solid #263245;
    transition:all .25s ease;
}

.metric-card:hover{
    border-color:#FF4DA7;
    box-shadow:0 0 12px rgba(255,77,167,.25);
    transform:translateY(-2px);
}

.metric-title{
    font-size:15px;
    color:#A9B4C2;
    margin-bottom:8px;
}

.metric-value{
    font-size:42px;
    font-weight:700;
    color:#F7F3EE;
}
</style>
""", unsafe_allow_html=True)


# HEADING
st.markdown("""
<style>
[data-testid="stHeaderActionElements"] {
    display: none;
}
</style>
            
<h1 style="
    font-size: 3.4rem;
    font-weight: 800;
    letter-spacing: -1px;
    margin: 0;
    line-height: 1.1;
    align: left;
"><span style="color:#FF4DA7;">V</span>Scholes</h1>

<h4 style="
    font-size: 1.25rem;
    color: #A9B4C2;
    margin: 0.2rem 0 0.6rem 0;
    line-height: 1.2;
">European Options Analytics</h4>

<p style="
    font-size: 1.0rem;
    color: #A9B4C2;
    margin: 0;
    line-height: 1.5;
">Price options, visualize Greeks, estimate implied volatility, and explore payoff profiles using the Black–Scholes model.</p>
""", unsafe_allow_html=True)



# SIDEBAR INPUT


with st.sidebar:
    stockOption = st.segmented_control("Price Source", ["Live Market", "Manual"], required=True, default="Live Market")

    stockInputcol1, stockInputcol2 = st.columns([0.08, 0.92])
    with stockInputcol2:
        if(stockOption=="Live Market"):
            stock = st.text_input("Enter Stock Symbol", value="RELIANCE").strip().upper()
            try:
                ticker = yf.Ticker(stock+".NS")
                S = ticker.fast_info["lastPrice"]
                if not S:
                    st.error("Stock Price is 0 or NaN. Please enter Current Stock Price MANUALLY.")
                    S = st.number_input ("Current Stock Price", value=100.00, min_value=0.00, step=0.5, format="%.2f")
                st.markdown(f"""
                    <h6 style="
        font-size: 1.15rem;
        color: #4ADE80;
        margin: 0.2rem 0 0.6rem 0;
        line-height: 1.2;
    ">Current Price: {S:.2f}</h6>
                """, unsafe_allow_html=True)
            except(KeyError, TypeError):
                st.error("Invalid ticker symbol. Please enter a valid NSE symbol.")
                S = st.number_input ("Current Stock Price MANUALLY", value=100.00, min_value=0.00, step=0.5, format="%.2f")
        else:
            S = st.number_input ("Current Stock Price", value=100.00, min_value=0.00, step=0.5, format="%.2f")

    K = st.number_input("Strike Price", value=100.00, min_value=1.00, step=0.50, format="%.2f")

    # T = st.date_input("Time to Expiry", value=date.today() + timedelta(days=7))
    timeOption = st.segmented_control("Time", ["Expiry Date", "Time to Expiry"], required=True, default="Expiry Date")
    timeInputcol1, timeInputcol2 = st.columns([0.08, 0.92])
    with timeInputcol2:
        if(timeOption=="Expiry Date"):
            T= st.date_input("Expiry Date", value=date.today() + timedelta(days=7), min_value=date.today() + timedelta(days=1))
            T = (T - date.today()).days / 365
        else:
            T = st.number_input("Time to Expiry (in days)", value=7, min_value=1, step=1)
            T = T / 365
    
    r = st.number_input("Risk-Free Rate (in %)", min_value=0.00, value=5.00, step=0.05, max_value=20.00)
    r=r/100

    sigma= st.number_input("Volatility (between 0 and 1)", min_value=0.01, value=0.20, step=0.01, max_value=1.00)


#FUNCTION CALLS

call_price, put_price = option_pricer(S, K, T, r, sigma)

greeksDict= greeksFunc(S, K, T, r, sigma)

#DISPLAYING OUTPUT


st.markdown("""
    <br>
    <h4 style="
        font-size: 1.25rem;
        color: #A9B4C2;
        margin: 1.5rem 0 0.8rem 0;
        line-height: 1.2;
    ">
    Option Prices
    </h4>
    """, unsafe_allow_html=True)


optionPriceCol1, optionPriceCol2 = st.columns(2, gap="small")

with optionPriceCol1:
    st.markdown(f"""
    <br>
    <div class="metric-card">
        <div class="metric-title">Call Option Price</div>
        <div class="metric-value">
        {call_price:.2f}
        </div>
    </div>
""", unsafe_allow_html=True)
    

with optionPriceCol2:
    st.markdown(f"""
    <br>
    <div class="metric-card">
        <div class="metric-title">Put Option Price</div>
        <div class="metric-value">
            {put_price:.2f}
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <br>
    <h4 style="
        font-size: 1.25rem;
        color: #A9B4C2;
        margin: 1.5rem 0 0.8rem 0;
        line-height: 1.2;
    ">Option Greek</h4>
    """, unsafe_allow_html=True)

deltaCallColumn, deltaPutColumn, gammaColumn = st.columns(3, gap="small")

with deltaCallColumn:
    st.markdown(f"""
        <br>
        <div class="metric-card">
        <div class="metric-title">Delta Call</div>
        <div class="metric-value">
        {greeksDict["delta_call"]:.2f}
        </div>
        </div>
    """, unsafe_allow_html=True)

with deltaPutColumn:
    st.markdown(f"""
        <br>
        <div class="metric-card">
        <div class="metric-title">Delta Put</div>
        <div class="metric-value">
        {greeksDict["delta_put"]:.2f}
        </div>
        </div>
    """, unsafe_allow_html=True)

with gammaColumn:
    st.markdown(f"""
        <br>
        <div class="metric-card">
        <div class="metric-title">Gamma</div>
        <div class="metric-value">
        {greeksDict["gamma"]:.4f}
        </div>
        </div>
    """, unsafe_allow_html=True)

thetaCallColumn, thetaPutColumn, vegaColumn = st.columns(3, gap="small")

with thetaCallColumn:
    st.markdown(f"""
        <br>
        <div class="metric-card">
        <div class="metric-title">Theta Call (per day)</div>
        <div class="metric-value">
        {greeksDict["theta_call"] :.2f}
        </div>
        </div>
    """, unsafe_allow_html=True)

with thetaPutColumn:
    st.markdown(f"""
        <br>
        <div class="metric-card">
        <div class="metric-title">Theta Put (per day)</div>
        <div class="metric-value">
        {greeksDict["theta_put"] :.2f}
        </div>
        </div>
    """, unsafe_allow_html=True)

with vegaColumn:
    st.markdown(f"""
        <br>
        <div class="metric-card">
        <div class="metric-title">Vega</div>
        <div class="metric-value">
        {greeksDict["vega"]:.2f}
        </div>
        </div>
    """, unsafe_allow_html=True)

rhoCall, rhoPut, xtraSpace = st.columns(3, gap="small")

with rhoCall:
    st.markdown(f"""
        <br>
        <div class="metric-card">
        <div class="metric-title">Rho Call</div>
        <div class="metric-value">
        {greeksDict["rho_call"]:.2f}
        </div>
        </div>
    """, unsafe_allow_html=True)

with rhoPut:
    st.markdown(f"""
        <br>
        <div class="metric-card">
        <div class="metric-title">Rho Put</div>
        <div class="metric-value">
        {greeksDict["rho_put"]:.2f}
        </div>
        </div>
    """, unsafe_allow_html=True)

