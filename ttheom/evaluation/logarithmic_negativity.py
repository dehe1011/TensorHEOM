import numpy as np

def getLogarithmicNegativity(rho, transposeQIdx):
    """Compute the logarithmic negativity of a multi-qubit density matrix.

    Parameters
    ----------
    rho : numpy.ndarray
        Density matrix of shape ``(2**N, 2**N)``.
        Row/column ordering: qubit ``N-1`` is the most significant index,
        qubit ``0`` is the least significant.
    transposeQIdx : list of int
        Indices of qubits on which the partial transpose is performed.

    Returns
    -------
    float
        Logarithmic negativity :math:`E_N(\\rho) = \\log_2 \\|\\rho^{T_A}\\|_1`.
    """

    numQ = int(np.log2(rho.shape[0]))

    tensorDims = [2] * 2 * numQ

    rhoTensor = rho.reshape(tensorDims)

    perm = np.arange(2*numQ)

    for q in transposeQIdx:
        rowAxis = numQ - 1 - q
        colAxis = rowAxis + numQ

        perm[rowAxis], perm[colAxis] = (perm[colAxis], perm[rowAxis])

    rhoTensorPartTrans = np.transpose(rhoTensor, perm)

    rhoPartTrans = rhoTensorPartTrans.reshape((2**numQ, 2**numQ))

    vals = np.linalg.svd(rhoPartTrans, compute_uv=False)

    traceNorm = np.sum(vals).real

    return np.log2(traceNorm)
