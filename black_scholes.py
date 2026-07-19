import numpy as np
from scipy.stats import norm

def option_pricer(S, K, T, r, sigma):

    d1= (np.log(S/K) + (r+ ((sigma**2)/2))*T) / (sigma * np.sqrt(T))

    d2 = d1 - (sigma * np.sqrt(T))

    call_price= (S * norm.cdf(d1)) - (K * np.exp(-1*r*T) * norm.cdf(d2))

    put_price= (K * np.exp(-1*r*T) * norm.cdf(-1*d2)) - (S * norm.cdf(-1*d1))

    call_price=np.round(call_price, 4)
    put_price=np.round(put_price,4)

    return call_price, put_price

call_price, put_price = option_pricer(42,40,0.5,0.10,0.20)
print(call_price, " ", put_price)