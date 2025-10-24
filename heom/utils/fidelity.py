import numpy as np

def getFidelity(rho, sigma):
    """compute fidelity

        args:
            rho, sigma (numpy.ndarray): density matrix:
                Hermitian matrix, positive semidefinite

        returns:
            fidelity
    """
    u, s, v = np.linalg.svd(rho)
    rhoSq = u @ np.diag(np.sqrt(s)) @ v

    u, s, v = np.linalg.svd(sigma)
    sigmaSq = u @ np.diag(np.sqrt(s)) @ v

    norm = np.linalg.norm(rhoSq@sigmaSq, ord='nuc')

    return norm**2