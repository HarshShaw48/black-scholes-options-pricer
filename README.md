# VScholes — Black-Scholes Options Pricer
Black-Scholes options pricer with Greeks calculator, payoff visualizer, sensitivity heatmap, and implied volatility solver. Built in Python + Streamlit.

## Live Demo


## Features

1. Black Scholes Call and Put price calculator, with live NSE market data that is fetched through yfinance. Just enter the Stock's Symbol. Default: RELIANCE
Current version has no support for BSE.

2. Greek Dashboard shows Delta, Gamma, Theta, Vega, Rho with per-day Theta, from the data entered by the user and fetched.

3. Sensitivity heatmap, helps visualise option price across spot and volatility ranges

4. Interactive payoff visualizer, helps visualise Long Call, Long Put, Short Call, Short Put, Bull Call Spread

5. Payoff summary, gives you an overview of the selected stratergy, by showing max profit, max loss, breakeven amount

6. Implied volatility solver, an additional feature. Its an bisection method and it back calculates IV from user entered market price.

## Black-Scholes Formula

## Limitations

Assumes European-style options.
Assumes constant volatility and interest rates.
Does not account for dividends.
Intended for educational and analytical purposes rather than live trading.