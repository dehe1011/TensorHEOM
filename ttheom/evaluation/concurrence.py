import numpy as np
from scipy.linalg import eigvals

def getConcurrence(rho):
    """Compute the concurrence of a two-qubit density matrix.

    Parameters
    ----------
    rho : numpy.ndarray
        Two-qubit density matrix of shape ``(4, 4)``;
        Hermitian, positive semidefinite.

    Returns
    -------
    float
        Concurrence :math:`C(\\rho) \\in [0, 1]`, where 0 means separable
        and 1 means maximally entangled.
    """
    sigma_y = np.array([[0, -1j], [1j, 0]])
    Y = np.kron(sigma_y, sigma_y)
    rho_tilde = Y @ rho.conj() @ Y
    R = rho @ rho_tilde

    eigenvals = np.sort(np.sqrt(np.abs(eigvals(R))))[::-1]
    C = max(0, eigenvals[0] - sum(eigenvals[1:]))
    return C
