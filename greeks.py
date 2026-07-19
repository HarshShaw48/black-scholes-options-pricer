import numpy as np
from scipy.stats import norm

def delta_call(S, K, T, r, sigma):
    d1=( np.log(S/K) + (r + ((sigma**2)/2))*T) / (sigma * np.sqrt(T))
    return(np.round((norm.cdf(d1)),4))

def delta_put(S, K, T, r, sigma):
    d1=( np.log(S/K) + (r + ((sigma**2)/2))*T) / (sigma * np.sqrt(T))
    return(np.round(((norm.cdf(d1))-1),4))

def gamma(S, K, T, r, sigma):
    d1=( np.log(S/K) + (r + ((sigma**2)/2))*T) / (sigma * np.sqrt(T))
    return(np.round((norm.pdf(d1)) / (S*sigma* np.sqrt(T)),4))


def theta_call(S, K, T, r, sigma):
    d1=( np.log(S/K) + (r + ((sigma**2)/2))*T) / (sigma * np.sqrt(T))
    d2 = d1 - (sigma * np.sqrt(T))
    term1= -(S*norm.pdf(d1)*sigma) / (2*np.sqrt(T))
    term2= r*K* np.exp(-1*r*T)* norm.cdf(d2)
    return(np.round(term1-term2,4))

def theta_put(S, K, T, r, sigma):
    d1=( np.log(S/K) + (r + ((sigma**2)/2))*T) / (sigma * np.sqrt(T))
    d2 = d1 - (sigma * np.sqrt(T))
    term1= -(S*norm.pdf(d1)*sigma) / (2*np.sqrt(T))
    term2= r*K* np.exp(-1*r*T)* norm.cdf(-d2)
    print(term1, term2)
    return(np.round(term1+term2,4))

def vega(S, K, T, r, sigma):
    d1=( np.log(S/K) + (r + ((sigma**2)/2))*T) / (sigma * np.sqrt(T))
    return(np.round((S*np.sqrt(T)*norm.pdf(d1)),4))


def rho_call(S, K, T, r, sigma):
    d1=( np.log(S/K) + (r + ((sigma**2)/2))*T) / (sigma * np.sqrt(T))
    d2 = d1 - (sigma * np.sqrt(T))
    return(np.round((K*T* np.exp(-1*r*T) * norm.cdf(d2)),4))

def rho_put(S, K, T, r, sigma):
    d1=( np.log(S/K) + (r + ((sigma**2)/2))*T) / (sigma * np.sqrt(T))
    d2 = d1 - (sigma * np.sqrt(T))
    return(np.round((-K*T* np.exp(-1*r*T) * norm.cdf(-d2)),4))




