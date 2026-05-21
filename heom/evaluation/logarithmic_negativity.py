import numpy as np

def getLogarithmicNegativity(rho, transposeQIdx):
    """compute logarithmic negativity

        args:
            rho (numpy.ndarray): density martix in the shape of 2^N x 2^N
                In the order of (N-1)th qubit, (N-2)th qubit, ... 0th qubit

        returns: logarithmic negativity
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