from abc import ABC, abstractmethod
import numpy as np

class TTs(ABC):
    """abstract class for MPS and MPO

        attributes:
            numQ (int): number of qubits
            numCore (int): number of cores
            numH (int): number of partial Hamiltonians
            dim (list): list of dimension of reservoir mode
            ptrKet, ptrBra (list): list of pointer to ket/bra vector of spin
            rho (numpy.ndarray): 1d array of tt.zTT (MPS)
            H (numpy.ndarray): 2d array of tt.zTT (MPO)
            omegaQSeq (numpy.ndarray): time sequence of qubit frequency
            pulse (list[
                    list[list[qubitIdx], pulse.abstract_pulse.abstractPulse]
                ]):
                list of class for pulse
            map (dict[tuple[int]: int]): dictionary for a mapping from
                qubit indeces to pulse indeces
                keys (tuple[int]): qubit indedes
                values (int): pulse indeces for self.pulse
            localPhase (list[float]): local phase of each qubit
                for virtual Z gates.
            indices (numpy.ndarray): 2d array of MPS indices
    """

    def __init__(self):
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
        self.localPhase = None
        self.indices = None

    def getRhoBondDims(self, rhoBondDims, levels, bondDim):
        """compute bond dimension of rhos

            params:
                rhoBondDims (numpy.ndarray): 2d array of bond dimensions
                levels (numpy.ndarray): 1d array of levels for each MPS
                bondDim (int): maximum bond dimension of MPS

            returns:
                rhoBondDims (numpy.ndarray): 2d array of bond dimensions
        """

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

    def createBathOperators(self, depth):
        """compute bath operators

            depth (list[int]): maximum hierarchy for each bath
            returns:
                num (list[np.ndarray]): 1d list of number operators
                cre (list[np.ndarray]): 1d list of creation operators
                ann (list[np.ndarray]): 1d list of annihilation operators
        """

        num = []
        cre  =[]
        ann = []

        for i in range(len(depth)):
            num.append(np.diag(np.arange(depth[i]+1)+0j))

            cre.append(np.zeros([depth[i]+1, depth[i]+1],
                                dtype=np.complex128))
            ann.append(np.zeros([depth[i]+1, depth[i]+1],
                                dtype=np.complex128))

            for j in range(cre[i].shape[0]-1):
                cre[i][j+1, j] = np.sqrt(j+1)
                ann[i][j, j+1] = np.sqrt(j+1)

        return num, cre, ann
        
    @abstractmethod
    def getPrefactors(self, dt: float, time: float, stepNum: int):
        pass