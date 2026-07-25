import numpy as np
from black_scholes import option_pricer

def implied_volatility(S, K, T, r, marketPrice, optionType):
    if marketPrice <= 0:
        return None, None, "Market price must be greater than zero."

    if(optionType=="Call"):
        intrinsic = max(S - K, 0)
    else:
        intrinsic = max(K - S, 0)

    if(marketPrice<intrinsic):
        return None, None, "Market price is below intrinsic value."

    low= 0.001
    high= 5.0
    tolerance= 1e-6
    maxIterations= 1000

    for iteration in range(maxIterations):
        mid = (low + high) /2
        callPrice, putPrice = option_pricer(S, K, T, r, mid)
        if(optionType=="Call"):
            bsPrice = callPrice
        else:
            bsPrice = putPrice

        if abs(bsPrice - marketPrice) < tolerance:
            return mid, iteration + 1, None

        if (bsPrice> marketPrice):
            high = mid
        else:
            low = mid

    return None, maxIterations, "Solver failed to converge."

