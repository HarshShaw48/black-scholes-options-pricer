import streamlit as st
from datetime import date, timedelta
import yfinance as yf
from black_scholes import option_pricer
from greeks import *
import plotly.graph_objects as go


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

    K = st.number_input("Strike Price", value=(S//100)*100, min_value=1.00, step=0.50, format="%.2f")

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

callPriceValue, putPriceValue = option_pricer(S, K, T, r, sigma)

greeksDict= greeksFunc(S, K, T, r, sigma)


#DISPLAYING OPTION PRICES

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
        {callPriceValue:.2f}
        </div>
    </div>
""", unsafe_allow_html=True)
    

with optionPriceCol2:
    st.markdown(f"""
    <br>
    <div class="metric-card">
        <div class="metric-title">Put Option Price</div>
        <div class="metric-value">
            {putPriceValue:.2f}
        </div>
    </div>
""", unsafe_allow_html=True)


#DISPLAYING OPTION GREEK

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
        <br>
    """, unsafe_allow_html=True)

# PAYOFF VISUALISER
st.markdown("""
<h4 style="
    font-size: 1.25rem;
    color: #A9B4C2;
    margin: 0.2rem 0 0.6rem 0;
    line-height: 1.2;
">Strategy Selector</h4>

<p style="
    font-size: 1.0rem;
    color: #A9B4C2;
    margin: 0;
    line-height: 1.5;
">Select an options strategy to visualize its payoff profile at expiration.</p>
<br>
""", unsafe_allow_html=True)


def createPayoffGraph (stockTimeT, payoff, stratergyName, strikes=None, breakEven=None):
    payoffGraph = go.Figure()
    payoffGraph.add_trace(
            go.Scatter(
                x= stockTimeT, y= payoff, mode= "lines", name= stratergyName, line= dict(color="#FF4DA7", width=3),
                hovertemplate=
                    "<b>Underlying Price</b>: %{x:.2f}<br>"
                    "<b>P/L</b>: %{y:.2f}<extra></extra>"
            )
        )
    
    payoffGraph.add_hline( y=0, line_dash="dash", line_color="#A9B4C2", opacity=0.7
        )
    
    # if strikes is not None:
    #     for i, strike in enumerate(strikes, start=1):
    #         payoffGraph.add_vline(
    #             x=strike,
    #             line_dash="dot",
    #             line_color="#4ADE80",
    #             annotation_text=f"Strike {i}",
    #             annotation_position="top"
    #         )

    y_min = payoff.min()
    y_max = payoff.max()
    padding = 0.05 * (y_max - y_min)
    if strikes is not None:
        for i, strike in enumerate(strikes, start=1):
            payoffGraph.add_trace(
                go.Scatter(
                    x=[strike, strike],
                    y=[y_min - padding, y_max + padding],
                    mode="lines",
                    line=dict(color="#4ADE80", dash="dot"),
                    name=f"Strike {i}",
                    hovertemplate=f"<b>Strike {i}</b>: {strike:.2f}<extra></extra>"
                )
            )
    
    x_min = stockTimeT.min()
    x_max = stockTimeT.max()

    # if breakEven is not None and x_min <= breakEven <= x_max:
    #     payoffGraph.add_vline(
    #         x=breakEven,
    #         line_dash="dash",
    #         line_color="#FFD166",
    #         annotation_text="Break-even",
    #         annotation_position="top"
    #     )

    if breakEven is not None and x_min <= breakEven <= x_max:
        payoffGraph.add_trace(
            go.Scatter(
                x=[breakEven, breakEven],
                y=[y_min - padding, y_max + padding],
                mode="lines",
                line=dict(color="#FFD166", dash="dash"),
                name="Break-even",
                hovertemplate=f"<b>Break-even</b>: {breakEven:.2f}<extra></extra>"
            )
        )
    
    payoffGraph.update_layout(
        title= stratergyName + " Payoff at Expiration",
        xaxis_title="Underlying Price at Expiration",
        yaxis_title="Profit / Loss",
        template="plotly_dark",
    
        paper_bgcolor="#0B1220",
        plot_bgcolor="#0B1220",
    
        font=dict(
            family="Inter",
            size=14,
            color="#F7F3EE"
        ),

        legend=dict(
            bgcolor="rgba(0,0,0,0)"
        ),

        hovermode="x unified",

        margin=dict(
            l=40,
            r=40,
            t=60,
            b=40
        )
    )
    
    payoffGraph.update_xaxes(
        showgrid=True,
        gridcolor="#263245",
        zeroline=False
    )
    
    payoffGraph.update_yaxes(
        showgrid=True,
        gridcolor="#263245",
        zeroline=False
    )
    
    st.plotly_chart(
        payoffGraph,
        width="stretch"
    )

payoffSelector = st.segmented_control ("options",["None", "Long Call", "Long Put", "Short Call", "Short Put", "Bull Call Spread"], label_visibility="collapsed", default="None")

if (payoffSelector == "None"):
    st.markdown("""
        <div style="
            background-color: rgba(255, 77, 167, 0.10);
            border: 1px solid #FF4DA7;
            border-radius: 10px;
            padding: 16px;
            color: #F7F3EE;
            text-align: center;
        ">
            Select an option strategy to view its payoff diagram.
        </div>
        """, unsafe_allow_html=True)

if (payoffSelector == "Long Call"):
    stockTimeT= np.linspace(0.5 * K, 1.5 * K, 300)
    payoff= np.maximum (stockTimeT - K, 0) - callPriceValue
    Breakeven = K + callPriceValue
    createPayoffGraph(stockTimeT, payoff, payoffSelector, [K], Breakeven)

elif(payoffSelector=="Long Put"):
    stockTimeT= np.linspace(0.5 * K, 1.5 * K, 300)
    payoff= np.maximum (K - stockTimeT, 0) - putPriceValue
    Breakeven= K - putPriceValue
    createPayoffGraph(stockTimeT, payoff, payoffSelector, [K], Breakeven)

elif (payoffSelector=="Short Call"):
    stockTimeT= np.linspace(0.5 * K, 1.5 * K, 300)
    payoff= callPriceValue - np.maximum (stockTimeT - K, 0)
    Breakeven= K + callPriceValue
    createPayoffGraph(stockTimeT, payoff, payoffSelector, [K], Breakeven)


elif (payoffSelector=="Short Put"):
    stockTimeT= np.linspace(0.5 * K, 1.5 * K, 300)
    payoff= putPriceValue - np.maximum (K - stockTimeT, 0)
    Breakeven= K - putPriceValue
    createPayoffGraph(stockTimeT, payoff, payoffSelector, [K], Breakeven)

elif (payoffSelector=="Bull Call Spread"):
    stockTimeT= np.linspace(0.5 * K, 1.5 * K, 300)
    K2 = st.number_input("Enter Second Strike Price", value=K*1.1, min_value=1.00, step=0.50, format="%.2f")
    callPriceValue_K2, _ = option_pricer(S, K2, T, r, sigma)
    netPremium= callPriceValue - callPriceValue_K2

    payoff= np.minimum(np.maximum(stockTimeT - K, 0), K2 - K) - netPremium
    Breakeven= K + netPremium

    createPayoffGraph(stockTimeT, payoff, payoffSelector, [K, K2], Breakeven)