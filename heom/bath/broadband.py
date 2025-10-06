import numpy as np

def broadbandNoise(bathParams, x):
    """compute broadband spectral noise power

        params:
            params (dict): parameter values for bath
                bathParams['beta'] (float): inverse temperature
                bathParams['omegaC'] (float): cutoff frequency
                bathParams['kappa'] (float): coupling strength
                bathParams['exp'] (float): spectral exponent
            x (numpy.ndarray): frequency points
                where the spectral noise power is calculated

            returns:
                numpy.ndarray: 
    """

    beta = bathParams['beta']
    omegaC = bathParams['omegaC']
    kappa = bathParams['kappa']
    exp = bathParams['exp']

    return (np.sign(x) * kappa * np.abs(x)**exp
            / (1. + (x / omegaC)**2)**2 / (1. - np.exp(-beta * x)))
