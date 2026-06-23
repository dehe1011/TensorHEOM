from abc import ABC, abstractmethod
import numpy as np
import copy

class TTs(ABC):
    """Abstract base class for the MPS/MPO tensor-train representation.

    Attributes
    ----------
    numQ : int
        Number of qubits.
    numCore : int
        Number of tensor-train cores.
    numH : int
        Number of partial Hamiltonian terms.
    dim : list
        Dimensions of the reservoir modes.
    ptrKet : list
        Pointers to the ket (row) indices of each spin.
    ptrBra : list
        Pointers to the bra (column) indices of each spin.
    rho : numpy.ndarray
        1-D array of :class:`~ttheom.tt.tt.zTT` cores representing the MPS.
    H : numpy.ndarray
        2-D array of :class:`~ttheom.tt.tt.zTT` cores representing the MPO.
    omegaQSeq : numpy.ndarray
        Time sequence of qubit frequencies.
    pulse : list
        List of ``[qubit_indices, abstractPulse]`` pairs.
    map : dict
        Mapping from qubit-index tuples to pulse indices in ``self.pulse``.
    matVZ : numpy.ndarray
        Matrix representation of the virtual Z gates.
    permMat : numpy.ndarray
        Permutation matrix for qubit reordering.
    shapeBathEye1 : list of tuple
        Shapes of bond-dimension-1 identity MPO cores for the bath modes.
    coreBathEye1 : list of numpy.ndarray
        Bond-dimension-1 identity MPO cores for the bath modes.
    shapeBathEye2 : list of tuple
        Shapes of bond-dimension-2 identity MPO cores for the bath modes.
    coreBathEye2 : list of numpy.ndarray
        Bond-dimension-2 identity MPO cores for the bath modes.
    shapeBathEye3 : list of tuple
        Shapes of bond-dimension-3 identity MPO cores for the bath modes.
    coreBathEye3 : list of numpy.ndarray
        Bond-dimension-3 identity MPO cores for the bath modes.
    """

    def __init__(self, depth):
        """Initialize the TTs base class and pre-build bath identity MPO cores.

        Parameters
        ----------
        depth : list of int
            Hierarchy depths of FP-HEOM for each bath mode
            (truncation at level ``depth[i]``).
        """

        self.numQ = None
        self.numCore = None
        self.numH = None
        self.dim = None
        self.ptrKet = None
        self.ptrBra = None
        self.rho = None
        self.H = None
        self.omegaQSeq = None
        self.pulse = None
        self.map = None
        self.matVZ = None
        self.permMat = None

        self.shapeBathEye1 = []
        self.coreBathEye1 = []
        self.shapeBathEye2 = []
        self.coreBathEye2 = []
        self.shapeBathEye3 = []
        self.coreBathEye3 = []

        for i in range(len(depth)):
            self.shapeBathEye1.append((1, depth[i]+1, depth[i]+1, 1))
            coreTmp = np.zeros(self.shapeBathEye1[i], dtype=np.complex128)
            coreTmp[0, :, :, 0] = np.eye(depth[i]+1)
            self.coreBathEye1.append(coreTmp.flatten(order='F'))

            self.shapeBathEye2.append((2, depth[i]+1, depth[i]+1, 2))
            coreTmp = np.zeros(self.shapeBathEye2[i], dtype=np.complex128)
            coreTmp[0, :, :, 0] = np.eye(depth[i]+1)
            coreTmp[1, :, :, 1] = np.eye(depth[i]+1)
            self.coreBathEye2.append(coreTmp.flatten(order='F'))

            self.shapeBathEye3.append((3, depth[i]+1, depth[i]+1, 3))
            coreTmp = np.zeros(self.shapeBathEye3[i], dtype=np.complex128)
            coreTmp[0, :, :, 0] = np.eye(depth[i]+1)
            coreTmp[1, :, :, 1] = np.eye(depth[i]+1)
            coreTmp[2, :, :, 2] = np.eye(depth[i]+1)
            self.coreBathEye3.append(coreTmp.flatten(order='F'))

    def getRhoBondDims(self, levels, bondDim):
        """Compute the bond dimensions for each MPS core.

        Parameters
        ----------
        levels : numpy.ndarray
            1-D array of local Hilbert-space dimensions for each core.
        bondDim : int
            Maximum allowed bond dimension.

        Returns
        -------
        rhoBondDims : numpy.ndarray
            2-D array of shape ``(numCore, 2)`` with left and right bond
            dimensions for each core.
        """

        rhoBondDims = np.zeros([self.numCore, 2], dtype=int)

        rhoBondDims[:, :] = 0
        rhoBondDims[0, 0] = 1
        rhoBondDims[self.numCore - 1, 1] = 1

        for i in range(self.numCore-1):
            row = rhoBondDims[i, 0] * levels[i]
            col = 1
            for j in range(i+1, self.numCore):
                col *= levels[j]
                if col > row:
                    break
            rhoBondDims[i, 1] = min(bondDim, row, col)
            rhoBondDims[i+1, 0] = rhoBondDims[i, 1]

        return rhoBondDims

    def setBathMPO(self, depth, nu, coeff, sysIdx, HIdx):
        """Build and store MPO cores for the system-bath interaction.

        Parameters
        ----------
        depth : int
            Maximum FP-HEOM hierarchy depth for this bath.
        nu : numpy.ndarray
            Poles of the bath correlation function decomposition.
        coeff : numpy.ndarray
            Residues of the bath correlation function decomposition.
        sysIdx : int
            Index used to look up ``ptrKet`` and ``ptrBra`` for the system site.
        HIdx : int
            Row index in ``self.H`` where the MPO cores will be stored.
        """

        dim  = len(nu)
        
        num = np.diag(np.arange(depth+1)+0j)

        cre = np.zeros([depth+1, depth+1], dtype=np.complex128)
        ann = np.zeros([depth+1, depth+1], dtype=np.complex128)

        for i in range(cre.shape[0]-1):
            cre[i+1, i] = np.sqrt(i+1)
            ann[i, i+1] = np.sqrt(i+1)

        coreTmp = np.zeros([4, depth+1, depth+1, 4], dtype=np.complex128)

        eye = np.eye(depth+1)

        for i in range(dim):
            k = self.ptrKet[sysIdx] + 2 * i + 1
            coreTmp.fill(0)
            coreTmp[0, :, :, 0] = eye
            coreTmp[1, :, :, 0] = nu[i] * num.T
            coreTmp[1, :, :, 1] = eye
            coreTmp[1, :, :, 2] = np.sqrt(coeff[i]) * ann.T
            coreTmp[2, :, :, 2] = eye
            coreTmp[3, :, :, 0] = np.sqrt(coeff[i]) * (cre.T - ann.T)
            coreTmp[3, :, :, 3] = eye

            self.setH(coreTmp, self.H[HIdx, k])

            k = self.ptrKet[sysIdx] + 2 * i + 2
            coreTmp.fill(0)
            coreTmp[0, :, :, 0] = eye
            coreTmp[1, :, :, 0] = nu[i].conj() * num.T
            coreTmp[1, :, :, 1] = eye
            coreTmp[1, :, :, 2] = np.sqrt(coeff[i].conj()) * (cre.T - ann.T)
            coreTmp[2, :, :, 2] = np.eye(depth+1)
            coreTmp[3, :, :, 0] = np.sqrt(coeff[i].conj()) * ann.T
            coreTmp[3, :, :, 3] = np.eye(depth+1)

            self.setH(coreTmp, self.H[HIdx, k])


    def setH(self, coreIn, TTOut):
        """Copy an MPO core array into a :class:`~ttheom.tt.tt.zTT` object.

        Parameters
        ----------
        coreIn : numpy.ndarray
            4-D MPO core array of shape
            ``(bondDimL, level, level, bondDimR)``.
        TTOut : tt.zTT
            Target MPO core object; overwritten in place.
        """

        TTOut.bondDimL = coreIn.shape[0]
        TTOut.bondDimR = coreIn.shape[3]
        TTOut.level = coreIn.shape[1]
        TTOut.core = copy.deepcopy(coreIn.flatten(order='F'))

    def setRefH(self, coreShape, coreFlattenIn, TTOut):
        """Set an MPO core by reference (no copy) from a flattened array.

        Parameters
        ----------
        coreShape : tuple
            Shape of the core before flattening,
            ``(bondDimL, level, level, bondDimR)``.
        coreFlattenIn : numpy.ndarray
            Flattened MPO core data; assigned by reference.
        TTOut : tt.zTT
            Target MPO core object; overwritten in place.
        """

        TTOut.bondDimL = coreShape[0]
        TTOut.bondDimR = coreShape[3]
        TTOut.level = coreShape[1]
        TTOut.core = coreFlattenIn

    @abstractmethod
    def getRDO(self):
        pass

    @abstractmethod
    def getPrefactors(self, dt: float, time: float, stepNum: int):
        pass