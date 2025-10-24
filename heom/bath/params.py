import numpy as np
from .broadband import broadbandNoise
from baryrat import aaa

def getBathParams(bathParams):
    """return bath parameters

        args:
            params (dict): parameter values for bath
                bathParams['type'] (str): bath type
                bathParams['tol'] (float): tolerance for the AAA algorithm

        returns:
            nu (list): list of poles for FP-HEOM
            coeff (list): list of residues for FP-HEOM
    """

    NUM_SAMPLE = 80000

    x = np.logspace(-6, 3, NUM_SAMPLE)
    x = np.concatenate((-x, x))
    x.sort()

    if bathParams['type'] == 'broadband':
        y = broadbandNoise(bathParams, x)

    r = aaa(x, y, tol=bathParams['tol'])

    pol, res = r.polres()

    mask = pol.imag < 0.0
    nu = pol[mask]
    coeff = res[mask]
    
    nu *= -1j
    coeff *= -2j * np.pi

    if np.isnan(nu).any() or np.isnan(coeff).any():
        raise ValueError('The decomposition ')

    return nu, coeff
