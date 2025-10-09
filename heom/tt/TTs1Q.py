import numpy as np
from scipy.linalg import qr
import copy
from .TTsTwoLevelId import TTsTwoLevelId
from .tt import zCreMPS, zTT
from ..tdevott import zRightOrth

class TTs1Q(TTsTwoLevelId):
    """ MPS and MPO for 1qubit systems
    """

    def __init__(self, rhoIni, bondDim, V, depth, nu, coeff,
                 pulse, pulseMap):
        """
            params:
                rhoIni (numpy.ndarray): initial reduced density operator
                bondDim (int): bondDimension of MPS
                V (numpy.ndarray):
                    matrices for qubit-reservoir coupling (3d array)
                nu (list): list of poles for FP-HEOM
                coeff (list): list of residues for FP-HEOM
                depth (list):
                    1d list of depth of hierarchy of FP-HEOM (from 0 to depth)
                pulse (list[
                    list[list[int], pulse.abstract_pulse.abstractPulse]
                    ]):
                    list for elemental gates
                pulseMap (dict[tuple[int]: int]):
                    dictionary for a mapping from
                    qubit indeces to pulse indeces
                    keys (tuple[int]): qubit indedes
                    values (int): pulse indeces for self.pulse
        """

        super().__init__(depth)

        self.dim = [nu[0].shape[0]]

        self.numQ = 1
        self.numCore = 2 * self.dim[0] + 2
        self.ptrKet = [0]
        self.ptrBra = [2*self.dim[0]+1]

        self.zGetMPS(rhoIni, bondDim, depth)

        zRightOrth(self.rho)

        self.numH = 4
        self.zGetMPO(V, depth, nu, coeff)

        self.indices = self.getIndices()

        self.pulse = pulse
        self.map = pulseMap

    def zGetMPS(self, rhoIni, bondDim, depth):
        """create MPS

            params:
                rhoIni (numpy.ndarray): initial reduced density operator
                bondDim (int): bondDimension of MPS
                depth (list):
                    1d list of depth of hierarchy of FP-HEOM (from 0 to depth)
        """
        
        levels = np.zeros(self.numCore, dtype=int)

        levels[self.ptrKet[0]] = 2
        levels[self.ptrKet[0] + 1:self.ptrBra[0]] = depth[0] + 1
        levels[self.ptrBra[0]] = 2

        rhoBondDims = self.getRhoBondDims(levels, bondDim)

        self.rho = zCreMPS(self.numCore, rhoBondDims, levels)

        ket0, bra0 = qr(rhoIni)

        i = self.ptrKet[0]
        coreTmp = np.zeros([self.rho[i].bondDimL,
                            self.rho[i].level,
                            self.rho[i].bondDimR],
                           dtype=np.complex128)
        coreTmp[0, :2, :2] = ket0
        self.rho[i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        i = self.ptrBra[0]
        coreTmp = np.zeros([self.rho[i].bondDimL,
                            self.rho[i].level,
                            self.rho[i].bondDimR],
                           dtype=np.complex128)
        coreTmp[:2, :2, 0] = bra0
        self.rho[i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        # middle tensors
        for i in range(self.ptrKet[0] + 1, self.ptrBra[0]):
            coreTmp = np.zeros([self.rho[i].bondDimL,
                                self.rho[i].level,
                                self.rho[i].bondDimR],
                               dtype=np.complex128)
            n = min(coreTmp.shape[0], coreTmp.shape[2])
            for j in range(n):
                coreTmp[j, 0, j] = 1.0 + 0.0j
            self.rho[i].core = copy.deepcopy(coreTmp.flatten(order='F'))

    def zGetMPO(self, V, depth, nu, coeff):
        """create MPO

            params:
                V (numpy.ndarray):
                    matrices for qubit-reservoir coupling (3d array)
                pol (list): list of poles for FP-HEOM
                res (list): list of residues for FP-HEOM
                depth (list):
                    1d list of depth of hierarchy of FP-HEOM (from 0 to depth)
        """
        # creare array of MPO
        self.H = np.array([[zTT() for _ in range(self.numCore)]
                           for _ in range(self.numH)])
        
        # set values for MPO
        # system part

        # time-independent part
        j = 0
        i = self.ptrKet[0]
        coreTmp = np.zeros([1, 2, 2, 4], dtype=np.complex128)
        coreTmp[0, :, :, 1] = self.sysEye
        coreTmp[0, :, :, 3] = V[0].T

        self.setH(coreTmp, self.H[j, i])

        i = self.ptrBra[0]
        coreTmp = np.zeros([4, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = self.sysEye
        coreTmp[2, :, :, 0] = V[0]

        self.setH(coreTmp, self.H[j, i])
        
        # time-dependent part
        # Zeeman splitting for qubit 1
        j = 1
        i = self.ptrKet[0]
        self.setRefH(self.shapeKet, self.coreKetSZ, self.H[j, i])

        i = self.ptrBra[0]
        self.setRefH(self.shapeBra, self.coreBraSZ, self.H[j, i])

        # drive for qubit 0 (cos)
        j = 2
        i = self.ptrKet[0]
        self.setRefH(self.shapeKet, self.coreKetSX, self.H[j, i])

        i = self.ptrBra[0]
        self.setRefH(self.shapeBra, self.coreBraSX, self.H[j, i])

        # drive for qubit 0 (sin)
        j = 3
        i = self.ptrKet[0]
        self.setRefH(self.shapeKet, self.coreKetSY, self.H[j, i])

        i = self.ptrBra[0]
        self.setRefH(self.shapeBra, self.coreBraSY, self.H[j, i])

        # reservoir
        # time-independent part
        j = 0
        for l in range(self.numQ):
            self.setBathMPO(depth[l], nu[l], coeff[l], l, j)

        l = 0
        # time-dependent part
        for j in range(1, 4):
            for i in range(self.ptrKet[l]+1, self.ptrBra[l]):
                self.setRefH(self.shapeBathEye2[l], self.coreBathEye2[l],
                             self.H[j, i])
    
    def getIndices(self):
        """compute MPS indices for output

            returns:
                indices (numpy.ndarray): 2d array of MPS indices
        """

        indices = np.zeros([4, self.numCore], dtype=np.int32)

        for i in range(4):
            qWiseIdx = [i//2 % 2, i % 2]
            indices[i, self.ptrKet[0]] = qWiseIdx[0]
            indices[i, self.ptrBra[0]] = qWiseIdx[1]

        return indices

    def getPrefactors(self, dt: float, time: float, stepNum: int)\
            -> np.ndarray:
        """compute prefactor terms for Runge-Kutta update

            params:
                dt (float): step size for Runge-Kutta integration
                time (float): current time
                stepNum (int): current step number of the integration
            
            returns:
                numpy.ndarray: prefactors corresponding to MPO
        """

        pulseIdx = self.map[(np.int64(0), )]
        preSX, preSY = self.pulse[pulseIdx][1].getPrefactor(dt, time, stepNum)

        return np.array(
            [dt, dt * self.omegaQSeq[0][stepNum], dt * preSX, dt * preSY])