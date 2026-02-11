import numpy as np
from scipy.linalg import eigvals

def getConcurrence(rho):

    sigma_y = np.array([[0, -1j], [1j, 0]])
    Y = np.kron(sigma_y, sigma_y)
    rho_tilde = Y @ rho.conj() @ Y
    R = rho @ rho_tilde

    eigenvals = np.sort(np.sqrt(np.abs(eigvals(R))))[::-1]
    C = max(0, eigenvals[0] - sum(eigenvals[1:]))
    return C