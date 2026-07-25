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

$$C = S \cdot N(d_1) - K e^{-rT} \cdot N(d_2)$$

$$P = K e^{-rT} \cdot N(-d_2) - S \cdot N(-d_1)$$

$$d_1 = \frac{\ln(S/K) + (r + \sigma^2/2)T}{\sigma\sqrt{T}}$$

$$d_2 = d_1 - \sigma\sqrt{T}$$

## The Greeks
| Greek | Formula | Meaning |
|-------|---------|---------|
| Delta | ∂C/∂S | Price change per ₹1 move in underlying |
| Gamma | ∂²C/∂S² | Rate of change of Delta |
| Theta | ∂C/∂T | Daily time decay of option value |
| Vega | ∂C/∂σ | Price change per 1% move in volatility |
| Rho | ∂C/∂r | Price change per 1% move in risk-free rate |


## Implied Volatility Solver
Implied Volatility (IV) is the value of volatility (σ) that makes the Black-Scholes model price equal to the option's actual market price. Instead of assuming a volatility value, the solver works backwards from the observed market price to find the volatility that best matches it. This gives an estimate of what the market is expecting in terms of future price movement.

The solver uses the Bisection Method to find the implied volatility. It starts with a lower bound of 0.001 and an upper bound of 5.0, then repeatedly checks the midpoint and narrows the range depending on whether the calculated option price is above or below the market price. This process continues until the difference is within a tolerance of 1 × 10⁻⁶, giving an accurate and stable estimate of the implied volatility.


## Limitations

- Assumes European-style options.
- Assumes constant volatility and interest rates.
- Does not account for dividends.
- Intended for educational and analytical purposes rather than live trading.
- Log-normal distribution of returns — assumes no jumps or fat tails
- NSE equity options are European-style, making BS appropriate here

## Tech Stack
- Python
- NumPy + SciPy
- Streamlit
- Plotly
- yfinance

## Project Structure
black-scholes-options-pricer/
│
├── app.py
├── black_scholes.py
├── greeks.py
├── iv_solver.py
├── requirements.txt
└── README.md

## Acknowledgements
- John C. Hull — Options, Futures, and Other Derivatives (primary mathematical reference)
- Chapters used: 9, 10, 12, 13, 14, 18, 19, 22
- VINDHYA SAHA, for constantly supporting me, always.
