import numpy as np
from baryrat import aaa
from .broadband import broadbandNoise

def getBathParams(bathParams):
    r"""
    Compute the pole–residue decomposition of a bath correlation function
    for FP-HEOM.

    The bath correlation function is assumed to admit an exponential
    decomposition of the form

    .. math::

        \begin{aligned}
        C(t)
        &= \langle X(t) X(0) \rangle_R,
        \\[4pt]
        C(t)
        &= \sum_{k=1}^{K} d_k\, e^{-z_k t},
        \end{aligned}

    where :math:`z_k` and :math:`d_k` denote the complex decay rates and
    coefficients, respectively.

    This routine samples the bath spectral function on a symmetric
    logarithmic frequency grid, constructs a rational approximation using
    the AAA algorithm, and converts the resulting poles and residues into
    the :math:`(z_k, d_k)` representation required by FP-HEOM.

    Currently, the bath spectral function is constructed for the
    ``"broadband"`` bath type via :func:`broadbandNoise`.

    Parameters
    ----------
    bathParams : dict
        Bath parameter dictionary. Required keys:

        - ``'type'`` (str): Bath type identifier. Currently supports ``'broadband'``.
        - ``'tol'`` (float): Tolerance passed to the AAA algorithm.

        Additional keys may be required depending on ``bathParams['type']``
        (e.g., broadband noise parameters used by :func:`broadbandNoise`).

    Returns
    -------
    nu : numpy.ndarray
        Complex frequencies :math:`z_k` (derived from the AAA poles).
    coeff : numpy.ndarray
        Complex coefficients :math:`d_k` (derived from the AAA residues).

    Notes
    -----
    - A symmetric grid :math:`x \in [-10^{3}, -10^{-6}] \cup [10^{-6}, 10^{3}]`
      with ``NUM_SAMPLE = 80000`` is used.
    - Only poles with negative imaginary part are retained before the FP-HEOM mapping.
    - The mapping applied is::

        nu    = -1j * pol
        coeff = -2j * np.pi * res

    Examples
    --------
    >>> bathParams = {'type': 'broadband', 'beta':5, 'kappa':0.004 / 2 / np.pi, 'omegaC':50, 'exp':1, 'tol':1e-6}
    >>> z, d = getBathParams(bathParams)
    """

    NUM_SAMPLE = 80000

    x = np.logspace(-6, 3, NUM_SAMPLE)
    x = np.concatenate((-x, x))
    x.sort()

    if bathParams['type'] == 'broadband':
        y = broadbandNoise(bathParams, x)

    else:
        raise ValueError(f"Unsupported bath type: {bathParams['type']}")

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
