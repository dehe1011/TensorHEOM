import numpy as np

def broadbandNoise(bathParams, x):
    r"""
    Compute the broadband spectral noise power :math:`S(\omega)`.

    The bath noise spectrum :math:`S(\omega)` is defined as

    .. math::

        S(\omega) = J(\omega)\,[1 + n(\omega)].

    Here :math:`n(\omega)` denotes the Bose–Einstein distribution

    .. math::

        n(\omega) = \frac{1}{e^{\beta \omega} - 1},

    and :math:`J(\omega)` denotes the broadband spectral density

    .. math::

        J(\omega) = \operatorname{sgn}(\omega)\, \frac{\kappa\,|\omega|^{s}}{\left[1 + \left(\omega/\omega_c\right)^2\right]^2}. 

    Parameters
    ----------
    bathParams : dict
        Bath parameters with the following keys:

        - ``'beta'`` (float): Inverse temperature :math:`\beta`.
        - ``'omegaC'`` (float): Cutoff frequency :math:`\omega_c`.
        - ``'kappa'`` (float): Coupling strength :math:`\kappa`.
        - ``'exp'`` (float): Spectral exponent :math:`s`.

    x : numpy.ndarray
        Frequency points :math:`\omega` at which :math:`S(\omega)` is evaluated.

    Returns
    -------
    numpy.ndarray
        Spectral noise power :math:`S(\omega)` evaluated at ``x``.

    Examples
    --------
    >>> bathParams = {'beta':5, 'kappa':0.004 / 2 / np.pi, 'omegaC':50, 'exp':1}
    >>> w = np.linspace(0.0, 50.0, 2000)
    >>> S = broadbandNoise(bathParams, w)
    """

    beta = bathParams['beta']
    omegaC = bathParams['omegaC']
    kappa = bathParams['kappa']
    exp = bathParams['exp']

    return (np.sign(x) * kappa * np.abs(x)**exp
            / (1. + (x / omegaC)**2)**2 / (1. - np.exp(-beta * x)))
