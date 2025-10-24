import copy
import numpy as np
from scipy.linalg import svd
from .TTsTwoLevelId import TTsTwoLevelId
from .tt import zCreMPS, zTT
from ..tdevott import zRightOrth

class TTsMQChainId(TTsTwoLevelId):
    """MPS and MPO for multi-qubit systems (independent reservoir)
        in the chain configuration
    """

    def __init__(self, numQ, rhoIni, bondDim, V, depth, nu, coeff,
                 pulse, pulseMap):
        """
            args:
                numQ (int): the number of qubits
                rhoIni (numpy.ndarray): initial reduced density operator
                bondDim (int): bondDimension of MPS
                omegaQ (numpy.ndarray): 1d array of qubit frequency
                J (list): list of coupling strength (len(J) = 1)
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

        self.dim = np.array([nu[i].shape[0] for i in range(len(nu))])

        self.numQ = numQ
        self.numCore = 2 * self.dim.sum() + 2 * self.numQ
        self.ptrKet = [2*i + 2*self.dim[:i].sum() for i in range(self.numQ)]
        self.ptrBra = [2*i+1 + 2*self.dim[:i+1].sum() 
                       for i in range(self.numQ)]

        self.zGetMPS(rhoIni, bondDim, depth)

        zRightOrth(self.rho)

        self.numH = 4 * self.numQ
        self.zGetMPO(V, depth, nu, coeff)

        self.pulse = pulse
        self.map = pulseMap

    def zGetMPS(self, rhoIni, bondDim, depth):
        """create MPS

            args:
                rhoIni (numpy.ndarray): initial reduced density operator
                bondDim (int): bondDimension of MPS
                depth (numpy.ndarray):
                    1d array of depth of hierarchy of FP-HEOM (from 0 to depth)
        """

        levels = np.zeros(self.numCore, dtype=int)

        for i in range(self.numQ):
            levels[self.ptrKet[i]] = 2
            levels[self.ptrKet[i]+1:self.ptrBra[i]] = depth[i] + 1
            levels[self.ptrBra[i]] = 2

        rhoBondDims = self.getRhoBondDims(levels, bondDim)

        self.rho = zCreMPS(self.numCore, rhoBondDims, levels)

        sysCores = SvdTT(self.numQ, rhoIni, bondDim)

        for i in range(self.numQ):
            ptr = self.ptrKet[i]
            rhoCoreShape = np.array([self.rho[ptr].bondDimL,
                                     self.rho[ptr].level,
                                     self.rho[ptr].bondDimR])
            coreTmp = np.zeros(rhoCoreShape, dtype=np.complex128)
            sysCore = sysCores[2*i]
            sysCoreShape = np.array(sysCore.shape)
            shape = np.minimum(rhoCoreShape, sysCoreShape)
            coreTmp[:shape[0], :shape[1], :shape[2]] = \
                sysCore[:shape[0], :shape[1], :shape[2]]
            self.rho[ptr].core = copy.deepcopy(coreTmp.flatten(order='F'))

            ptr = self.ptrBra[i]
            rhoCoreShape = np.array([self.rho[ptr].bondDimL,
                                     self.rho[ptr].level,
                                     self.rho[ptr].bondDimR])
            coreTmp = np.zeros(rhoCoreShape, dtype=np.complex128)
            sysCore = sysCores[2*i+1]
            sysCoreShape = np.array(sysCore.shape)
            shape = np.minimum(rhoCoreShape, sysCoreShape)
            coreTmp[:shape[0], :shape[1], :shape[2]] = \
                sysCore[:shape[0], :shape[1], :shape[2]]
            self.rho[ptr].core = copy.deepcopy(coreTmp.flatten(order='F'))

            for j in range(self.ptrKet[i]+1, self.ptrBra[i]):
                coreTmp = np.zeros([self.rho[j].bondDimL,
                                    self.rho[j].level,
                                    self.rho[j].bondDimR],
                                   dtype=np.complex128)
                n = min(coreTmp.shape[0], coreTmp.shape[2])
                for k in range(n):
                    coreTmp[k, 0, k] = 1.0 + 0.0j
                self.rho[j].core = copy.deepcopy(coreTmp.flatten(order='F'))

    def zGetMPO(self, V, depth, nu, coeff):
        """create MPO

            args:
                omegaQ (numpy.ndarray): 1d array of qubit frequency
                J (list): list of coupling strength between two qubits
                V (numpy.ndarray):
                    matrices for qubit-reservoir coupling (3d array)
                pol (list): list of poles for FP-HEOM
                res (list): list of residues for FP-HEOM
                depth (list):
                    1d list of depth of hierarchy of FP-HEOM (from 0 to depth)
        """

        # create array of MPO
        self.H = np.array([[zTT() for _ in range(self.numCore)]
                           for _ in range(self.numH)])
        
        # set values for MPO
        # system part
        # time-independent part
        j = 0

        i = 0
        ptr = self.ptrKet[i]
        coreTmp = np.zeros([1, 2, 2, 4], dtype=np.complex128)
        coreTmp[0, :, :, 1] = self.sysEye
        coreTmp[0, :, :, 3] = V[i].T
        self.setH(coreTmp, self.H[j, ptr])

        for i in range(1, self.numQ):
            ptr = self.ptrKet[i]
            coreTmp = np.zeros([2, 2, 2, 4], dtype=np.complex128)
            coreTmp[0, :, :, 0] = self.sysEye
            coreTmp[1, :, :, 1] = self.sysEye
            coreTmp[1, :, :, 3] = V[i].T
            self.setH(coreTmp, self.H[j, ptr])

        for i in range(0, self.numQ-1):
            ptr = self.ptrBra[i]
            coreTmp = np.zeros([4, 2, 2, 2], dtype=np.complex128)
            coreTmp[0, :, :, 0] = self.sysEye
            coreTmp[1, :, :, 1] = self.sysEye
            coreTmp[2, :, :, 0] = V[i]
            self.setH(coreTmp, self.H[j, ptr])

        i = self.numQ-1
        ptr = self.ptrBra[i]
        coreTmp = np.zeros([4, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = self.sysEye
        coreTmp[2, :, :, 0] = V[i]
        self.setH(coreTmp, self.H[j, ptr])

        # single-qubit gate
        for l in range(self.numQ):
            # ket and bra vectors with operation
            ptrKetTmp = self.ptrKet[l]
            ptrBraTmp = self.ptrBra[l]

            # Zeeman splitting
            j = 3 * l + 1
            self.setRefH(self.shapeKet, self.coreKetSZ, self.H[j, ptrKetTmp])
            self.setRefH(self.shapeBra, self.coreBraSZ, self.H[j, ptrBraTmp])
            # drive (cos)
            j = 3 * l + 2
            self.setRefH(self.shapeKet, self.coreKetSX, self.H[j, ptrKetTmp])
            self.setRefH(self.shapeBra, self.coreBraSX, self.H[j, ptrBraTmp])
            # drive (sin)
            j = 3 * l + 3
            self.setRefH(self.shapeKet, self.coreKetSY, self.H[j, ptrKetTmp])
            self.setRefH(self.shapeBra, self.coreBraSY, self.H[j, ptrBraTmp])

            # ket and bra vectors without operation
            st = 3 * l + 1
            en = 3 * l + 4
            for k in list(range(l)) + list(range(l+1, self.numQ)):
                for i in [self.ptrKet[k], self.ptrBra[k]]:
                    for j in range(st, en):
                        self.setRefH(self.shapeSysEye1, self.coreSysEye1,
                                     self.H[j, i])
                        
        # two-qubit gate
        for l in range(self.numQ-1):
            j = 3 * self.numQ + l + 1

            # ket and bra vectors with operation
            ptrKetTmp1 = self.ptrKet[l]
            ptrBraTmp1 = self.ptrBra[l]
            ptrKetTmp2 = self.ptrKet[l+1]
            ptrBraTmp2 = self.ptrBra[l+1]

            self.setRefH(self.shapeJKet1, self.coreJKet1,
                         self.H[j, ptrKetTmp1])
            self.setRefH(self.shapeJBra1, self.coreJBra1,
                         self.H[j, ptrBraTmp1])
            self.setRefH(self.shapeJKet2, self.coreJKet2,
                         self.H[j, ptrKetTmp2])
            self.setRefH(self.shapeJBra2, self.coreJBra2,
                         self.H[j, ptrBraTmp2])

            # ket and bra vectors without operation
            for k in list(range(l)) + list(range(l+2, self.numQ)):
                for i in [self.ptrKet[k], self.ptrBra[k]]:
                    self.setRefH(self.shapeSysEye1, self.coreSysEye1,
                                 self.H[j, i])
                    
        # reservoir
        # time-independent part
        j = 0
        for l in range(self.numQ):
            self.setBathMPO(depth[l], nu[l], coeff[l], l, j)

        # single-qubit gate
        for l in range(self.numQ):
            st = 3 * l + 1
            en = 3 * l + 4

            # reservoir for qubit without operation
            for k in list(range(l)) + list(range(l+1, self.numQ)):
                for j in range(st, en):
                    for i in range(self.ptrKet[k]+1, self.ptrBra[k]):
                        self.setRefH(self.shapeBathEye1[k],
                                     self.coreBathEye1[k], self.H[j, i])

            # reservoir for qubit with operation
            for j in range(st, en):
                for i in range(self.ptrKet[l]+1, self.ptrBra[l]):
                    self.setRefH(self.shapeBathEye2[l], self.coreBathEye2[l],
                                 self.H[j, i])

        # two-qubit gate
        for l in range(self.numQ-1):
            j = 3 * self.numQ + l + 1

            # reservoir for qubit without operation
            for k in list(range(l)) + list(range(l+2, self.numQ)):
                for i in range(self.ptrKet[k]+1, self.ptrBra[k]):
                    self.setRefH(self.shapeBathEye1[k],
                                 self.coreBathEye1[k], self.H[j, i])
                    
            # reservoir for qubit with operation
            for k in [l, l+1]:
                for i in range(self.ptrKet[k]+1, self.ptrBra[k]):
                    self.setRefH(self.shapeBathEye3[k],
                                 self.coreBathEye3[k], self.H[j, i])
                    
    def getPrefactors(self, dt: float, time: float, stepNum: int)\
            -> np.ndarray:
        """compute prefactor terms for Runge-Kutta update

            args:
                dt (float): step size for Runge-Kutta integration
                time (float): current time
                stepNum (int): current step number of the integration
            
            returns:
                numpy.ndarray: prefactors corresponding to MPO
        """
        # time-independent part
        prefactors = [dt]

        # single-qubit gate
        for i in range(self.numQ):
            prefactors.append(dt * self.omegaQSeq[i][stepNum])

            pulseIdx = self.map[(np.int64(self.numQ - i - 1), )]
            preSX, preSY = \
                self.pulse[pulseIdx][1].getPrefactor(dt, time, stepNum)

            prefactors.append(dt * preSX)
            prefactors.append(dt * preSY)

        # two-qubit gate
        for i in range(self.numQ-1):
            pulseIdx = self.map[(np.int64(self.numQ-i-2),
                                 np.int64(self.numQ-i-1))]
            preJ = self.pulse[pulseIdx][1].getPrefactor(dt, time, stepNum)

            prefactors.append(dt * preJ)

        return np.array(prefactors)
    
def SvdTT(numQ, rhoIni, bondDim):
    """Singular value decomposition of initial reduced density operator

        args:
            numQ (int): the number of qubits
            rhoIni (numpy.ndarray): 2**numQ x 2**numQ matrix for system
            bondDim (int): maximum bond dimension of MPS

        returns:
            coreList (list[numpy.ndarray])
    """

    LEVEL = 2 # each qubit: two-level systems

    rhoSize = 4**numQ
    rhoTmp = np.zeros(rhoSize, dtype=np.complex128)
    
    formatSpec = f'0{2*numQ}b'
    for i in range(rhoSize):
        binaryIdx = format(i, formatSpec)
        binaryRowIdx = binaryIdx[-1::-2]
        binaryClmIdx = binaryIdx[-2::-2]
        
        rowIdx = int(binaryRowIdx, 2)
        clmIdx = int(binaryClmIdx, 2)

        rhoTmp[i] = rhoIni[rowIdx, clmIdx]

    coreList = []
    
    bondDimL = 1

    for i in range(2*numQ-1):
        rhoTmp = rhoTmp.reshape([bondDimL*LEVEL, -1], order='F')
        U, s, Vh = svd(rhoTmp, full_matrices=False)

        bondDimR = min(U.shape[1], bondDim)
        core = U[:, :bondDimR]
        coreList.append(core.reshape([bondDimL, LEVEL, bondDimR], order='F'))
        
        rhoTmp = (np.diag(s) @ Vh)[:bondDimR, :]

        bondDimL = bondDimR

    coreList.append(rhoTmp.reshape([bondDimL, LEVEL, 1], order='F'))

    return coreList