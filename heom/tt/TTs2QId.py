import copy
import numpy as np
from scipy.linalg import qr
from .TTs import TTs
from .tt import zCreMPS, zTT
from ..tdevott import zRightOrth

class TTs2QId(TTs):
    """MPS and MPO for 2qubit systems (independent reservoir)
    """

    def __init__(self, rhoIni, bondDim, V, depth, nu, coeff,
                 pulse, pulseMap):
        """
            params:
                rhoIni (numpy.ndarray): initial reduced density operator
                bondDim (int): bondDimension of MPS
                omegaQ (numpy.ndarray): 1d array of qubit frequency
                J (list):  list of coupling strength (len(J) = 1)
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

        super().__init__()
        
        self.dim = [nu[i].shape[0] for i in range(len(nu))]

        self.numQ = 2
        self.numCore = 2 * self.dim[0] + 2 * self.dim[1] + 4
        self.ptrKet = [0, 2*self.dim[0] + 2]
        self.ptrBra = [2*self.dim[0] + 1, 2*self.dim[0] + 2*self.dim[1] + 3]

        self.zGetMPS(rhoIni, bondDim, depth)

        zRightOrth(self.rho)

        self.numH = 8
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
        rhoBondDims = np.zeros([self.numCore, 2], dtype=int)
        
        levels[self.ptrKet[0]] = 2
        levels[self.ptrKet[0] + 1:self.ptrBra[0]] = depth[0] + 1
        levels[self.ptrBra[0]] = 2
        levels[self.ptrKet[1]] = 2
        levels[self.ptrKet[1] + 1:self.ptrBra[1]] = depth[1] + 1
        levels[self.ptrBra[1]] = 2

        rhoBondDims[:, :] = 0
        rhoBondDims[0, 0] = 1
        rhoBondDims[self.numCore - 1, 1] = 1

        rhoBondDims = self.getRhoBondDims(rhoBondDims, levels, bondDim)

        self.rho = zCreMPS(self.numCore, rhoBondDims, levels)

        ket0, bra0, ket1, bra1 = QRTT(rhoIni)

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
        coreTmp[:2, :2, :4] = bra0.reshape([2, 2, 4], order='F')
        self.rho[i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        i = self.ptrKet[1]
        coreTmp = np.zeros([self.rho[i].bondDimL,
                            self.rho[i].level,
                            self.rho[i].bondDimR],
                           dtype=np.complex128)
        coreTmp[:4, :2, :2] = ket1.reshape([4, 2, 2], order='F')
        self.rho[i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        i = self.ptrBra[1]
        coreTmp = np.zeros([self.rho[i].bondDimL,
                            self.rho[i].level,
                            self.rho[i].bondDimR],
                           dtype=np.complex128)
        coreTmp[:2, :2, 0] = bra1
        self.rho[i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        # middle tensors
        for i in list(range(self.ptrKet[0] + 1, self.ptrBra[0])) \
                + list(range(self.ptrKet[1] + 1, self.ptrBra[1])):
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
                omegaQ (numpy.ndarray): 1d array of qubit frequency
                J (list): list of coupling strength between two qubits
                V (numpy.ndarray):
                    matrices for qubit-reservoir coupling (3d array)
                pol (list): list of poles for FP-HEOM
                res (list): list of residues for FP-HEOM
                depth (list):
                    1d list of depth of hierarchy of FP-HEOM (from 0 to depth)
        """
        # system Hamiltonian
        sZ = np.array([[1.0,  0.0],
                    [0.0, -1.0]], dtype=np.complex128)

        sX = np.array([[0.0,  1.0],
                    [1.0,  0.0]], dtype=np.complex128)

        sY = np.array([[0.0 , -1.0j],
                    [1.0j,  0.0 ]], dtype=np.complex128)

        sP = np.array([[0.0, 1.0],
                    [0.0, 0.0]], dtype=np.complex128)

        sM = np.array([[0.0, 0.0],
                    [1.0, 0.0]], dtype=np.complex128)

        # creare array of MPO
        self.H = np.array([[zTT() for _ in range(self.numCore)]
                           for _ in range(self.numH)])

        # set values for MPO
        # system part
        eye = np.eye(sZ.shape[0])
        # time-independent part
        j = 0
        i = self.ptrKet[0]
        coreTmp = np.zeros([1, 2, 2, 4], dtype=np.complex128)
        coreTmp[0, :, :, 1] = eye
        coreTmp[0, :, :, 3] = V[0].T

        self.setH(coreTmp, self.H[j, i])

        i = self.ptrBra[0]
        coreTmp = np.zeros([4, 2, 2, 2], dtype=np.complex128)
        coreTmp[0, :, :, 0] = eye
        coreTmp[1, :, :, 1] = eye
        coreTmp[2, :, :, 0] = V[0]

        self.setH(coreTmp, self.H[j, i])

        i = self.ptrKet[1]
        coreTmp = np.zeros([2, 2, 2, 4], dtype=np.complex128)
        coreTmp[0, :, :, 0] = eye
        coreTmp[1, :, :, 1] = eye
        coreTmp[1, :, :, 3] = V[1].T

        self.setH(coreTmp, self.H[j, i])

        i = self.ptrBra[1]
        coreTmp = np.zeros([4, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = eye
        coreTmp[2, :, :, 0] = V[1]

        self.setH(coreTmp, self.H[j, i])

        # System Hamiltonians
        # ket vector with operation
        coreTmp = np.zeros([1, 2, 2, 2], dtype=np.complex128)
        coreTmp[0, :, :, 1] = eye

        # Zeeman splitting (j = 1, 4)
        coreTmp[0, :, :, 0] = 0.5j * sZ.T
        for l in range(self.numQ):
            i = self.ptrKet[l]
            j = 3 * l + 1
            self.setH(coreTmp, self.H[j, i])

        # drive (cos, j = 2, 5)
        coreTmp[0, :, :, 0] = -0.5j * sX.T
        for l in range(self.numQ):
            i = self.ptrKet[l]
            j = 3 * l + 2
            self.setH(coreTmp, self.H[j, i])

        # drive (sin, j = 3, 6)
        coreTmp[0, :, :, 0] = -0.5j * sY.T
        for l in range(self.numQ):
            i = self.ptrKet[l]
            j = 3 * l + 3
            self.setH(coreTmp, self.H[j, i])

        # bra vector with operation
        coreTmp = np.zeros([2, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = eye

        # Zeeman splitting (j = 1, 4)
        coreTmp[1, :, :, 0] = -0.5j * sZ
        for l in range(self.numQ):
            i = self.ptrBra[l]
            j = 3 * l + 1
            self.setH(coreTmp, self.H[j, i])

        # drive (cos, j = 2, 5)        
        coreTmp[1, :, :, 0] = 0.5j * sX
        for l in range(self.numQ):
            i = self.ptrBra[l]
            j = 3 * l + 2
            self.setH(coreTmp, self.H[j, i])

        # drive (sin, j = 3, 6)
        coreTmp[1, :, :, 0] = 0.5j * sY
        for l in range(self.numQ):
            i = self.ptrBra[l]
            j = 3 * l + 3
            self.setH(coreTmp, self.H[j, i])

        # ket and bra vectors without operation
        coreTmp = np.zeros([1, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = eye

        for l in range(self.numQ):
            st = 3 * l + 1
            en = 3 * l + 4
            for k in list(range(l)) + list(range(l+1, self.numQ)):
                for i in [self.ptrKet[k], self.ptrBra[k]]:
                    for j in range(st, en):
                        self.setH(coreTmp, self.H[j, i])

        # direct coupling
        j = 7
        i = self.ptrKet[0]
        coreTmp = np.zeros([1, 2, 2, 3], dtype=np.complex128)
        coreTmp[0, :, :, 0] = eye
        coreTmp[0, :, :, 1] = -1j * sP.T
        coreTmp[0, :, :, 2] = -1j * sM.T

        self.setH(coreTmp, self.H[j, i])

        i = self.ptrBra[0]
        coreTmp = np.zeros([3, 2, 2, 4], dtype=np.complex128)
        coreTmp[0, :, :, 2] = sP
        coreTmp[0, :, :, 3] = sM
        coreTmp[1, :, :, 0] = eye
        coreTmp[2, :, :, 1] = eye

        self.setH(coreTmp, self.H[j, i])

        i = self.ptrKet[1]
        coreTmp = np.zeros([4, 2, 2, 3], dtype=np.complex128)
        coreTmp[0, :, :, 0] = sM.T
        coreTmp[1, :, :, 0] = sP.T
        coreTmp[2, :, :, 1] = eye
        coreTmp[3, :, :, 2] = eye

        self.setH(coreTmp, self.H[j, i])

        i = self.ptrBra[1]
        coreTmp = np.zeros([3, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = eye
        coreTmp[1, :, :, 0] = 1j * sM
        coreTmp[2, :, :, 0] = 1j * sP

        self.setH(coreTmp, self.H[j, i])

        # reservoir
        # time-independent part
        j = 0
        for l in range(self.numQ):
            self.setBathMPO(depth[l], nu[l], coeff[l], l, j)

        # direct coupling
        j = 7
        for l in range(self.numQ):
            coreTmp = np.zeros([3, depth[l]+1, depth[l]+1, 3],
                               dtype=np.complex128)
            coreTmp[0, :, :, 0] = np.eye(depth[l]+1)
            coreTmp[1, :, :, 1] = np.eye(depth[l]+1)
            coreTmp[2, :, :, 2] = np.eye(depth[l]+1)

            for i in range(self.ptrKet[l]+1, self.ptrBra[l]):
                self.setH(coreTmp, self.H[j, i])

        # reservoir
        # single-qubit operation
        for l in range(self.numQ):
            st = 3 * l + 1
            en = 3 * l + 4

            # reservoir for qubit without operation
            for k in list(range(l)) + list(range(l+1, self.numQ)):
                coreTmp = np.zeros([1, depth[k]+1, depth[k]+1, 1],
                                   dtype=np.complex128)
                coreTmp[0, :, :, 0] = np.eye(depth[k]+1)
                
                for j in range(st, en):
                    for i in range(self.ptrKet[k]+1, self.ptrBra[k]):
                        self.setH(coreTmp, self.H[j, i])

            # reservoir for qubit with operation
            coreTmp = np.zeros([2, depth[l]+1, depth[l]+1, 2],
                               dtype=np.complex128)
            coreTmp[0, :, :, 0] = np.eye(depth[l]+1)
            coreTmp[1, :, :, 1] = np.eye(depth[l]+1)

            for j in range(st, en):
                for i in range(self.ptrKet[l]+1, self.ptrBra[l]):
                    self.setH(coreTmp, self.H[j, i])

    def getIndices(self):
        """compute MPS indices for output

            returns:
                indices (numpy.ndarray): 2d array of MPS indices
        """

        indices = np.zeros([16, self.numCore], dtype=np.int32)

        for i in range(16):
            qWiseIdx = [i//8 % 2, i//4 % 2, i//2 % 2, i % 2]
            indices[i, self.ptrKet[0]] = qWiseIdx[0]
            indices[i, self.ptrKet[1]] = qWiseIdx[1]
            indices[i, self.ptrBra[0]] = qWiseIdx[2]
            indices[i, self.ptrBra[1]] = qWiseIdx[3]

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
        preSX0, preSY0 = \
            self.pulse[pulseIdx][1].getPrefactor(dt, time, stepNum)
        
        pulseIdx = self.map[(np.int64(1), )]
        preSX1, preSY1 = \
            self.pulse[pulseIdx][1].getPrefactor(dt, time, stepNum)
        
        pulseIdx = self.map[(np.int64(0), np.int64(1))]
        preJ = self.pulse[pulseIdx][1].getPrefactor(dt, time, stepNum)

        return np.array([dt,
                         dt * self.omegaQSeq[0][stepNum],
                         dt * preSX1,
                         dt * preSY1,
                         dt * self.omegaQSeq[1][stepNum],
                         dt * preSX0,
                         dt * preSY0,
                         dt * preJ])


def QRTT(rhoIni):
    """QR decomposition of initial reduced density operator

        params:
            rhoIni (numpy.ndarray): 4x4 matrix for system

        returns:
            ket0, bra0, ket1, bra1 (numpy.ndarray)
    """

    indices = ([[0, 1, 0, 1], [2, 3, 2, 3], [0, 1, 0, 1], [2, 3, 2, 3]],
               [[0, 0, 1, 1], [0, 0, 1, 1], [2, 2, 3, 3], [2, 2, 3, 3]])
    rhoTmp = rhoIni[indices].reshape([2, 8], order='F')
    
    ket0, r1 = qr(rhoTmp, mode='economic')
    r1 = r1.reshape([4, 4], order='F')

    bra0, r2 = qr(r1, mode='economic')
    r2 = r2.reshape([8, 2], order='F')
    
    ket1, bra1 = qr(r2, mode='economic')
    
    return ket0, bra0, ket1, bra1
