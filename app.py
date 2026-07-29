import streamlit as st
from datetime import date, timedelta
import yfinance as yf
from black_scholes import option_pricer
from greeks import *
import plotly.graph_objects as go
from iv_solver import implied_volatility


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

[data-testid="stIconMaterial"] {
    font-family: "Material Symbols Rounded" !important;
    font-weight: normal !important;
    font-style: normal !important;
    font-size: 24px;
}

.metric-card {
    padding: 1.125rem;  
    border-radius: 1.125rem;  
    background: #141D2E;
    border: 0.0625rem solid #263245;
    transition: all .25s ease;
}

.metric-card:hover{
    border-color: #FF4DA7;
    box-shadow: 0 0 0.75rem rgba(255,77,167,.25);
    transform: translateY(-0.125rem);
}

.metric-title{
    font-size: 0.9375rem;  
    color: #A9B4C2;
    margin-bottom: 0.5rem; 
}

.metric-value{
    font-size: 2rem;   
    font-weight: 700;
    color: #F7F3EE;
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




# FETCHING HISTORICAL DATA 
@st.cache_data(ttl=3600)
def historicalVolatility(ticker, period="3mo", window=30):
    data = yf.download(
        ticker,
        period=period,
        progress=False,
        auto_adjust=True
    )

    close = data["Close"].iloc[:, 0]
    returns = np.log(close / close.shift(1)).dropna()
    histVol = returns.tail(window).std() * np.sqrt(252) * 100
    return float(histVol)


# SIDEBAR INPUT

with st.sidebar:
    stockOption = st.segmented_control("Price Source", ["Live Market", "Manual"], required=True, default="Live Market")

    stockInputcol1, stockInputcol2 = st.columns([0.08, 0.92])
    histVol = None
    with stockInputcol2:
        if(stockOption=="Live Market"):
            stock = st.text_input("Enter Stock Symbol", value="RELIANCE").strip().upper()
            try:
                ticker = yf.Ticker(stock+".NS")
                S = ticker.fast_info["lastPrice"]
                histVol = historicalVolatility(stock + ".NS")
                history = ticker.history(period="1d")
                lastTime = history.index[-1]
                formatted_time = lastTime.strftime("%d %b %Y, %I:%M %p")
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
    <h6 style="
            font-size: 0.82rem;
            color: #4ADE80;
            margin: 0 0 0.6rem 0;
            line-height: 1.2;
        ">As of {formatted_time}</h6>
                """, unsafe_allow_html=True)
            except(KeyError, TypeError):
                st.error("Invalid ticker symbol. Please enter a valid NSE symbol.")
                S = st.number_input ("Current Stock Price MANUALLY", value=100.00, min_value=0.00, step=0.5, format="%.2f")
        else:
            S = st.number_input ("Current Stock Price", value=100.00, min_value=0.00, step=0.5, format="%.2f")
        st.caption(
    "This model uses the standard Black-Scholes assumptions and does not account for dividends. "
    "Option prices for dividend-paying stocks may differ from market prices."
)

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
    
    r = st.number_input("Risk-Free Rate (in %)", min_value=0.00, value=5.25, step=0.05, max_value=20.00)
    r=r/100
    st.caption("Defaulted to the current RBI repo rate (5.25%). Update manually if required.")

    if histVol is not None:
        sigma= st.number_input("Volatility (between 0 and 1)", min_value=0.01, value=min(max(histVol/100, 0.01), 1.00), step=0.01, max_value=1.00)
        st.caption(f"30-Day Historical Volatility: {histVol:.2f}% or {histVol/100:.2f}")
        st.caption("Computed from the last 30 trading days using Yahoo Finance.")
    else:
        sigma= st.number_input("Volatility (between 0 and 1)", min_value=0.01, value=(0.20), step=0.01, max_value=1.00)
        st.caption("30-Day Historical Volatility unavailable.")


#FUNCTION CALLS

callPriceValue, putPriceValue = option_pricer(S, K, T, r, sigma)

greeksDict= greeksFunc(S, K, T, r, sigma)


#DISPLAYING OPTION PRICES

st.markdown("""
    <br>
    <br>
    <h4 style="
        font-size: 1.25rem;
        margin: 0.2rem 0 0.6rem 0;
        # color: #A9B4C2;
        line-height: 1.2;
    ">Option Prices</h4>
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
    <br>
    <h4 style="
        font-size: 1.25rem;
        # color: #A9B4C2;
        margin: 0.2rem 0 0.6rem 0;
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

if greeksDict["theta_call"] < 0:
    callThetaText = f"Call option loses approximately ₹{abs(greeksDict["theta_call"]):.2f}/day due to time decay."
else:
    callThetaText = f"Call option gains approximately ₹{greeksDict["theta_call"]:.2f}/day."

if greeksDict["theta_put"] < 0:
    putThetaText = f"Put option loses approximately ₹{abs(greeksDict["theta_put"]):.2f}/day due to time decay."
else:
    putThetaText = f"Put option gains approximately ₹{greeksDict["theta_put"]:.2f}/day."


with thetaCallColumn:
    st.markdown(f"""
        <br>
        <div class="metric-card">
        <div class="metric-title">Theta Call (per day)</div>
        <div class="metric-value">
        {greeksDict["theta_call"] :.2f}
        </div>
        <div class="metric-title">{callThetaText}</div>
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
        <div class="metric-title">{putThetaText}</div>
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


# HEATMAP

st.markdown("""
<br>
<h4 style="
    font-size: 1.25rem;
    margin: 0.2rem 0 0.6rem 0;
    # color: #A9B4C2;
    line-height: 1.2;
">Sensitivity Heatmap</h4>

<p style="
    font-size: 1.0rem;
    color: #A9B4C2;
    margin: 0;
    line-height: 1.5;
">Explore how option prices shift across a range of spot prices and volatilities.</p>
<br>
""", unsafe_allow_html=True)

heatmapType = st.segmented_control ("options",["Call", "Put"], label_visibility="collapsed", default="Call", selection_mode="single", required=True)


spotPrices = np.round(np.linspace(0.70*S, 1.30*S, 20),4)
volatilities= np.round(np.linspace(0.05, 0.80, 20),4)

prices=[]
for j in volatilities:
    currentRow=[]
    for i in spotPrices:
        X,Y=option_pricer(i, K, T, r, j)
        if(heatmapType=="Call"):
            currentRow.append(X)
        else:
            currentRow.append(Y)
    prices.append(currentRow)

heatMap= go.Figure()

heatMap.add_trace(go.Heatmap(x= spotPrices, y= volatilities, z= prices, colorscale="Plasma", 
colorbar=dict(title=f"{heatmapType} Price (₹)", thickness=18, len=0.8), 
hovertemplate=
f"<b>Underlying Price</b>: ₹%{{x:.2f}}<br>"
f"<b>Volatility</b>: %{{y:.1%}}<br>"
f"<b>{heatmapType} Price</b>: ₹%{{z:.2f}}"
"<extra></extra>", xgap=1, ygap=1))

heatMap.add_trace(
    go.Scatter(
        x=[K, K],
        y=[volatilities.min(), volatilities.max()],
        mode="lines",
        line=dict(
            color="#FF4DA7",
            width=2.5,
            dash="dash"
        ),
        opacity=1,
        name="Strike Price"
    )
)

heatMap.add_trace(
    go.Scatter(
        x=[S, S],
        y=[volatilities.min(), volatilities.max()],
        mode="lines",
        line=dict(
            color="#4ADE80",
            width=2
        ),
        name="Spot Price"
    )
)

heatMap.add_annotation(
    x=K,
    y=volatilities.max(),
    text=f"Strike (₹{K:.2f})",
    showarrow=True,
    arrowhead=2,
    arrowsize=1,
    arrowwidth=2,
    arrowcolor="#FF4DA7",
    ax=0,
    ay=-35,
    bgcolor="#141D2E",
    bordercolor="#FF4DA7",
    borderwidth=1,
    font=dict(
        color="#F7F3EE",
        size=12
    )
)

heatMap.add_annotation(
    x=S,
    y=volatilities.max(),
    text=f"Spot (₹{S:.2f})",
    showarrow=True,
    arrowhead=2,
    arrowsize=1,
    arrowwidth=2,
    arrowcolor="#4ADE80",
    ax=65,
    ay=-10,
    bgcolor="#141D2E",
    bordercolor="#4ADE80",
    borderwidth=1,
    font=dict(
        color="#F7F3EE",
        size=12
    )
)

heatMap.update_layout(
    xaxis_title="Underlying Price (₹)",
    yaxis_title="Volatility (σ)", 
    title=f"{heatmapType} Price Sensitivity Heatmap",
    height=550,
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        title="Underlying Price (₹)"
    ),
    yaxis=dict(
        showgrid=False,
        zeroline=False,
        title="Volatility (σ)",
        tickformat=".0%"
    ),
    margin=dict(
        l=40,
        r=20,
        t=60,
        b=40
    ),
    paper_bgcolor="#0B1220",
    plot_bgcolor="#0B1220",
    font=dict(
        color="#F7F3EE"
    )
    )


st.plotly_chart(heatMap, width="stretch")

# PAYOFF VISUALISER
st.markdown("""
<br>
<h4 style="
    font-size: 1.25rem;
        # color: #A9B4C2;
    margin: 0.2rem 0 0.6rem 0;
    line-height: 1.2;
">Payoff Visualizer</h4>

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

payoffSelector = st.segmented_control ("options",["None", "Long Call", "Long Put", "Short Call", "Short Put", "Bull Call Spread"], label_visibility="collapsed", default="None", required=True)

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

##METRIC CHART

if (payoffSelector != "None"):
    st.markdown("""
    <br>
    <h4 style="
        font-size: 1.25rem;
        # color: #A9B4C2;
        margin: 0.2rem 0 0.6rem 0;
        line-height: 1.2;
    ">Payoff Summary</h4>

    <p style="
        font-size: 1.0rem;
        color: #A9B4C2;
        margin: 0;
        line-height: 1.5;
    ">Key risk and reward levels for your selected strategy at expiration.</p>
    <br>
    """, unsafe_allow_html=True)

if(payoffSelector == "Long Call"):
    longCallCard1, longCallCard2, longCallCard3 = st.columns(3, gap="small")

    with longCallCard1:
        st.markdown(f"""
            <br>
            <div class="metric-card">
                <div class="metric-title">Max Profit</div>
                <div class="metric-value">
                Unlimited
                </div>
            </div>
        """, unsafe_allow_html=True)

    with longCallCard2:
        st.markdown(f"""
            <br>
            <div class="metric-card">
                <div class="metric-title">Max Loss</div>
                <div class="metric-value">
                {callPriceValue:.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with longCallCard3:
        st.markdown(f"""
            <br>
            <div class="metric-card">
                <div class="metric-title">Breakeven</div>
                <div class="metric-value">
                {Breakeven:.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)

elif(payoffSelector == "Long Put"):
    longPutCard1, longPutCard2, longPutCard3 = st.columns(3, gap="small")

    with longPutCard1:
        st.markdown(f"""
            <br>
            <div class="metric-card">
                <div class="metric-title">Max Profit</div>
                <div class="metric-value">
                {K - putPriceValue:.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with longPutCard2:
        st.markdown(f"""
            <br>
            <div class="metric-card">
                <div class="metric-title">Max Loss</div>
                <div class="metric-value">
                {putPriceValue:.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with longPutCard3:
        st.markdown(f"""
            <br>
            <div class="metric-card">
                <div class="metric-title">Breakeven</div>
                <div class="metric-value">
                {Breakeven:.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)

elif(payoffSelector == "Short Call"):
    shortCallCard1, shortCallCard2, shortCallCard3 = st.columns(3, gap="small")

    with shortCallCard1:
        st.markdown(f"""
            <br>
            <div class="metric-card">
                <div class="metric-title">Max Profit</div>
                <div class="metric-value">
                {callPriceValue:.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with shortCallCard2:
        st.markdown(f"""
            <br>
            <div class="metric-card">
                <div class="metric-title">Max Loss</div>
                <div class="metric-value">
                Unlimited
                </div>
            </div>
        """, unsafe_allow_html=True)

    with shortCallCard3:
        st.markdown(f"""
            <br>
            <div class="metric-card">
                <div class="metric-title">Breakeven</div>
                <div class="metric-value">
                {Breakeven:.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)

elif(payoffSelector == "Short Put"):
    shortPutCard1, shortPutCard2, shortPutCard3 = st.columns(3, gap="small")

    with shortPutCard1:
        st.markdown(f"""
            <br>
            <div class="metric-card">
                <div class="metric-title">Max Profit</div>
                <div class="metric-value">
                {putPriceValue:.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with shortPutCard2:
        st.markdown(f"""
            <br>
            <div class="metric-card">
                <div class="metric-title">Max Loss</div>
                <div class="metric-value">
                Unlimited
                </div>
            </div>
        """, unsafe_allow_html=True)

    with shortPutCard3:
        st.markdown(f"""
            <br>
            <div class="metric-card">
                <div class="metric-title">Breakeven</div>
                <div class="metric-value">
                {Breakeven:.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)

elif(payoffSelector == "Bull Call Spread"):
    bullCallCard1, bullCallCard2, bullCallCard3 = st.columns(3, gap="small")

    with bullCallCard1:
        st.markdown(f"""
            <br>
            <div class="metric-card">
                <div class="metric-title">Max Profit</div>
                <div class="metric-value">
                {(K2-K-netPremium):.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with bullCallCard2:
        st.markdown(f"""
            <br>
            <div class="metric-card">
                <div class="metric-title">Max Loss</div>
                <div class="metric-value">
                {(netPremium):.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with bullCallCard3:
        st.markdown(f"""
            <br>
            <div class="metric-card">
                <div class="metric-title">Breakeven</div>
                <div class="metric-value">
                {Breakeven:.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)


#IV CALCULATOR
st.markdown("""
<br>
<h4 style="
    font-size: 1.25rem;
    margin: 0.2rem 0 0.6rem 0;
    # color: #A9B4C2;
    line-height: 1.2;
">Implied Volatility Solver</h4>

<p style="
    font-size: 1.0rem;
    color: #A9B4C2;
    margin: 0;
    line-height: 1.5;
">Enter a market-observed option price to back-calculate the implied volatility using the Black-Scholes model.</p>
<br>
""", unsafe_allow_html=True)

optionType = st.segmented_control("Option Type",["None", "Call", "Put"], default="None", selection_mode="single", required=True)

if optionType != "None":
    ivCol1, ivCol2 = st.columns([0.8, 0.2])

    with ivCol1:
        marketPrice= st.number_input("Market Option Price (₹)", min_value=0.0, step=0.01, format="%.2f", value= (callPriceValue if optionType=="Call" else putPriceValue))

    with ivCol2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        calculateIV = st.button("Calculate", width="stretch")

    if calculateIV:
        with st.spinner("Calculating implied volatility..."):
            iv, iterations, error = implied_volatility(S, K, T, r, marketPrice, optionType)

        if error:
            st.error(error)

        else:
            ivValueCol1, ivValueCol2 = st.columns(2)

            with ivValueCol1:
                st.markdown(f"""
                    <br>
                    <div class="metric-card">
                    <div class="metric-title">Implied Volatility</div>
                    <div class="metric-value">{iv*100:.2f}%
                    </div>
                    </div>
                """, unsafe_allow_html=True)

            with ivValueCol2:
                st.markdown(f"""
                    <br>
                    <div class="metric-card">
                    <div class="metric-title">Iterations</div>
                    <div class="metric-value">{iterations:.0f}
                    </div>
                    </div>
                """, unsafe_allow_html=True)

st.markdown("""
<br>
<div style="
    background-color:#FF4DA71A;
    border:1px solid #FF4DA7;
    border-radius:10px;
    padding:20px;
    color:#F7F3EE;
">

<h2 style="
    color:#FF4DA7;
    text-align:center;
    margin-top:0;
    margin-bottom:1rem;
">
About VScholes
</h2>

<p style="
    font-size:1rem;
    line-height:1.8;
    text-align:justify;
    margin-bottom:1rem;
">
<b>VScholes</b> was built by <span style="color:#FF4DA7;"><b>Harsh Shaw</b></span>, a Computer Science student at
<b>Techno India University, Kolkata</b>, as part of a self learning journey into
fin-tech. The project implements Black-Scholes option pricing, Greeks, implied volatility, and payoff analysis from scratch using
<b>Python, NumPy, SciPy, and Streamlit</b>.
</p>

<p style="
    font-size:1rem;
    line-height:1.8;
    text-align:justify;
    margin-bottom:1rem;
">
This is the second project in a series focused on quantitative finance and derivatives.
The next project explores implied volatility surfaces and term structure using live
options chain data.
</p>

<p style="
    text-align:center;
    font-size:0.96rem;
    margin-bottom:1.6rem;
">
<b>LinkedIn:</b>
<a href="https://www.linkedin.com/in/harsh-shaw-111330248/"
target="_blank"
style="color:#FF4DA7; text-decoration:none; font-weight:600;">
linkedin.com/in/harsh-shaw-111330248
</a>
</p>

<p style="
    text-align:center;
    color:#B8B8B8;
    font-style:italic;
    font-size:0.92rem;
    margin:0;
">
Special thanks to <span style="color:#FF4DA7;"><b>Vindhya Saha</b></span> for her constant support and encouragement throughout this journey.
</p>

</div>
""", unsafe_allow_html=True)