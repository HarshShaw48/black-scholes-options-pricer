import numpy as np
from scipy.stats import norm

def delta_call(S, K, T, r, sigma):
    d1=( np.log(S/K) + (r + ((sigma**2)/2))*T) / (sigma * np.sqrt(T))
    return((norm.cdf(d1)))

def delta_put(S, K, T, r, sigma):
    d1=( np.log(S/K) + (r + ((sigma**2)/2))*T) / (sigma * np.sqrt(T))
    return(((norm.cdf(d1))-1))

def gamma(S, K, T, r, sigma):
    d1=( np.log(S/K) + (r + ((sigma**2)/2))*T) / (sigma * np.sqrt(T))
    return((norm.pdf(d1)) / (S*sigma* np.sqrt(T)))


def theta_call(S, K, T, r, sigma):
    d1=( np.log(S/K) + (r + ((sigma**2)/2))*T) / (sigma * np.sqrt(T))
    d2 = d1 - (sigma * np.sqrt(T))
    term1= -(S*norm.pdf(d1)*sigma) / (2*np.sqrt(T))
    term2= r*K* np.exp(-1*r*T)* norm.cdf(d2)
    return(term1-term2)

def theta_put(S, K, T, r, sigma):
    d1=( np.log(S/K) + (r + ((sigma**2)/2))*T) / (sigma * np.sqrt(T))
    d2 = d1 - (sigma * np.sqrt(T))
    term1= -(S*norm.pdf(d1)*sigma) / (2*np.sqrt(T))
    term2= r*K* np.exp(-1*r*T)* norm.cdf(-d2)
    print(term1, term2)
    return(term1+term2)

def vega(S, K, T, r, sigma):
    d1=( np.log(S/K) + (r + ((sigma**2)/2))*T) / (sigma * np.sqrt(T))
    return((S*np.sqrt(T)*norm.pdf(d1)))


def rho_call(S, K, T, r, sigma):
    d1=( np.log(S/K) + (r + ((sigma**2)/2))*T) / (sigma * np.sqrt(T))
    d2 = d1 - (sigma * np.sqrt(T))
    return((K*T* np.exp(-1*r*T) * norm.cdf(d2)))

def rho_put(S, K, T, r, sigma):
    d1=( np.log(S/K) + (r + ((sigma**2)/2))*T) / (sigma * np.sqrt(T))
    d2 = d1 - (sigma * np.sqrt(T))
    return((-K*T* np.exp(-1*r*T) * norm.cdf(-d2)))


def greeksFunc(S, K, T, r, sigma):
    return({"delta_call": delta_call(S, K, T, r, sigma),
    "delta_put": delta_put(S, K, T, r, sigma),
    "gamma": gamma(S, K, T, r, sigma),
    "theta_call": theta_call(S, K, T, r, sigma)/365,
    "theta_put": theta_put(S, K, T, r, sigma)/365,
    "vega": vega(S, K, T, r, sigma)/100,
    "rho_call": rho_call(S, K, T, r, sigma)/100,
    "rho_put": rho_put(S, K, T, r, sigma)/100})


