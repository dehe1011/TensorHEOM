from abc import ABC, abstractmethod
import numpy as np
import copy

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
                    list[list[int], pulse.abstract_pulse.abstractPulse]
                ]):
                list of class for pulse
            map (dict[tuple[int]: int]): dictionary for a mapping from
                qubit indeces to pulse indeces
                keys (tuple[int]): qubit indedes
                values (int): pulse indeces for self.pulse
            localPhase (list[float]): local phase of each qubit
                for virtual Z gates.
            indices (numpy.ndarray): 2d array of MPS indices

            shapeBathEye1 (list[tuple]):
                shapes of MPO cores for identity operators acting on baths
                bond dimension = 1
            coreBathEye1 (list[numpy.ndarray]):
                MPO cores for identity operators action on baths
                bond dimension = 1
            shapeBathEye2 (list[tuple]):
                shapes of MPO cores for identity operators acting on baths
                bond dimension = 2
            coreBathEye2 (list[numpy.ndarray]):
                MPO cores for identity operators action on baths
                bond dimension = 2
            shapeBathEye3 (list[tuple]):
                shapes of MPO cores for identity operators acting on baths
                bond dimension = 3
            coreBathEye3 (list[numpy.ndarray]):
                MPO cores for identity operators action on baths
                bond dimension = 3
    """

    def __init__(self, depth):
        """params:
            depth (list):
                1d list of depth of hierarchy of FP-HEOM (from 0 to depth)
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
        self.localPhase = None
        self.indices = None

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
        """compute bond dimension of rhos

            params:
                rhoBondDims (numpy.ndarray): 2d array of bond dimensions
                levels (numpy.ndarray): 1d array of levels for each MPS
                bondDim (int): maximum bond dimension of MPS

            returns:
                rhoBondDims (numpy.ndarray): 2d array of bond dimensions
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
        """compute MPO cores
            set values to self.H

            params:
                depth (int): maximum hierarchy for bath
                nu (numpy.ndarray): poles for FP-HEOM
                coeff (numpy.ndarray): residues for FP-HEOM
                sysIdx (int): system index for ptrKet and ptrBra
                HIdx (int): MPO index
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
        """set values to MPO cores,
            by copying values from coreIn to TTOut
        
            params:
                coreIn (numpy.ndarray): MPO core for input
                TTOut (tt.zTT): MPO for output, overwritten
        """

        TTOut.bondDimL = coreIn.shape[0]
        TTOut.bondDimR = coreIn.shape[3]
        TTOut.level = coreIn.shape[1]
        TTOut.core = copy.deepcopy(coreIn.flatten(order='F'))

    def setRefH(self, coreShape, coreFlattenIn, TTOut):
        """set values to MPO cores,
            by referring to values of coreFlattenIn

            params:
                coreShape (tuple): shape of core before flattening 
                coreFlattenIn (numpy.ndarray): MPO core for input
                TTOut (tt.zTT): MPO for output, overwritten
        """

        TTOut.bondDimL = coreShape[0]
        TTOut.bondDimR = coreShape[3]
        TTOut.level = coreShape[1]
        TTOut.core = coreFlattenIn


    @abstractmethod
    def getPrefactors(self, dt: float, time: float, stepNum: int):
        pass