import numpy as np

def getFidelity(rho, sigma):
    """Compute the quantum state fidelity between two density matrices.

    Parameters
    ----------
    rho : numpy.ndarray
        Density matrix; Hermitian, positive semidefinite.
    sigma : numpy.ndarray
        Density matrix; Hermitian, positive semidefinite.

    Returns
    -------
    float
        Fidelity :math:`F(\\rho, \\sigma) = \\left(\\operatorname{tr}\\sqrt{\\sqrt{\\rho}\\,\\sigma\\sqrt{\\rho}}\\right)^2`.
    """
    u, s, v = np.linalg.svd(rho)
    rhoSq = u @ np.diag(np.sqrt(s)) @ v

    u, s, v = np.linalg.svd(sigma)
    sigmaSq = u @ np.diag(np.sqrt(s)) @ v

    norm = np.linalg.norm(rhoSq@sigmaSq, ord='nuc')

    return norm**2
