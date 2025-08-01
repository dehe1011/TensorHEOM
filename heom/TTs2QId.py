import copy
import numpy as np
from scipy.linalg import qr
from .TTs import TTs
from .tt import zCreMPS, zTT
from .tdevott import zRightOrth

class TTs2QId(TTs):
    """MPS and MPO for 2qubit systems (independent reservoir)
    """

    def __init__(self, rhoIni, bondDim, omegaQ, J, V, depth, nu, coeff):
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
        """

        super().__init__()
        
        self.dim = [nu[i].shape[0] for i in range(len(nu))]

        self.numCore = 2 * self.dim[0] + 2 * self.dim[1] + 4
        self.ptrKet = [0, 2*self.dim[0] + 2]
        self.ptrBra = [2*self.dim[0] + 1, 2*self.dim[0] + 2*self.dim[1] + 3]

        self.zGetMPS(rhoIni, bondDim, depth)

        zRightOrth(self.rho)

        self.zGetMPO(omegaQ, J, V, depth, nu, coeff)

        self.indices = self.getIndices()        

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

        for i in range(self.numCore-1):
            row = rhoBondDims[i, 0] * levels[i]
            col = 1
            for j in range(i+1, self.numCore):
                col *= levels[j]
                if col > row:
                    break
            rhoBondDims[i, 1] = min(bondDim, row, col)
            rhoBondDims[i+1, 0] = rhoBondDims[i, 1]

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

    def zGetMPO(self, omegaQ, J, V, depth, nu, coeff):
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

        # creare array of MPO
        self.H = np.array([[zTT() for _ in range(self.numCore)]
                           for _ in range(5)])

        # set values for MPO
        # system part
        # time-independent part
        j = 0
        i = self.ptrKet[0]
        coreTmp = np.zeros([1, 2, 2, 6], dtype=np.complex128)
        coreTmp[0, :, :, 0] = -0.5j * omegaQ[0] * sZ.T
        coreTmp[0, :, :, 1] = np.eye(sZ.shape[0])
        coreTmp[0, :, :, 3] = V[0].T
        coreTmp[0, :, :, 4] = -1j * J[0] * sP.T
        coreTmp[0, :, :, 5] = -1j * J[0] * sM.T

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        i = self.ptrBra[0]
        coreTmp = np.zeros([6, 2, 2, 6], dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(sZ.shape[0])
        coreTmp[1, :, :, 0] = 0.5j * omegaQ[0] * sZ
        coreTmp[1, :, :, 1] = np.eye(sZ.shape[0])
        coreTmp[1, :, :, 4] = sP
        coreTmp[1, :, :, 5] = sM
        coreTmp[2, :, :, 0] = V[0]
        coreTmp[4, :, :, 2] = np.eye(sZ.shape[0])
        coreTmp[5, :, :, 3] = np.eye(sZ.shape[0])

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        i = self.ptrKet[1]
        coreTmp = np.zeros([6, 2, 2, 6], dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(sZ.shape[0])
        coreTmp[1, :, :, 0] = -0.5j * omegaQ[1] * sZ.T
        coreTmp[1, :, :, 1] = np.eye(sZ.shape[0])
        coreTmp[1, :, :, 3] = V[1].T
        coreTmp[2, :, :, 0] = sM.T
        coreTmp[3, :, :, 0] = sP.T
        coreTmp[4, :, :, 4] = np.eye(sZ.shape[0])
        coreTmp[5, :, :, 5] = np.eye(sZ.shape[0])

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        i = self.ptrBra[1]
        coreTmp = np.zeros([6, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(sZ.shape[0])
        coreTmp[1, :, :, 0] = 0.5j * omegaQ[1] * sZ
        coreTmp[2, :, :, 0] = V[1]
        coreTmp[4, :, :, 0] = 1j * J[0] * sM
        coreTmp[5, :, :, 0] = 1j * J[0] * sP

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        # drive for qubit 1 (cos)
        j = 1
        i = self.ptrKet[0]
        coreTmp = np.zeros([1, 2, 2, 2], dtype=np.complex128)
        coreTmp[0, :, :, 0] = -0.5j * sX.T
        coreTmp[0, :, :, 1] = np.eye(sZ.shape[0])

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        i = self.ptrBra[0]
        coreTmp = np.zeros([2, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(sZ.shape[0])
        coreTmp[1, :, :, 0] = 0.5j * sX

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        i = self.ptrKet[1]
        coreTmp = np.zeros([1, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(sZ.shape[0])

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        i = self.ptrBra[1]
        coreTmp = np.zeros([1, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(sZ.shape[0])

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        # drive for qubit 1 (sin)
        j = 2
        i = self.ptrKet[0]
        coreTmp = np.zeros([1, 2, 2, 2], dtype=np.complex128)
        coreTmp[0, :, :, 0] = -0.5j * sY.T
        coreTmp[0, :, :, 1] = np.eye(sZ.shape[0])

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        i = self.ptrBra[0]
        coreTmp = np.zeros([2, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(sZ.shape[0])
        coreTmp[1, :, :, 0] = 0.5j * sY

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        i = self.ptrKet[1]
        coreTmp = np.zeros([1, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(sZ.shape[0])

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        i = self.ptrBra[1]
        coreTmp = np.zeros([1, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(sZ.shape[0])

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        # drive for qubit 2 (cos)
        j = 3
        i = self.ptrKet[0]
        coreTmp = np.zeros([1, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(sZ.shape[0])

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        i = self.ptrBra[0]
        coreTmp = np.zeros([1, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(sZ.shape[0])

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        i = self.ptrKet[1]
        coreTmp = np.zeros([1, 2, 2, 2], dtype=np.complex128)
        coreTmp[0, :, :, 0] = -0.5j * sX.T
        coreTmp[0, :, :, 1] = np.eye(sZ.shape[0])

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        i = self.ptrBra[1]
        coreTmp = np.zeros([2, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(sZ.shape[0])
        coreTmp[1, :, :, 0] = 0.5j * sX

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        # drive for qubit 2 (sin)
        j = 4
        i = self.ptrKet[0]
        coreTmp = np.zeros([1, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(sZ.shape[0])

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        i = self.ptrBra[0]
        coreTmp = np.zeros([1, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(sZ.shape[0])

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        i = self.ptrKet[1]
        coreTmp = np.zeros([1, 2, 2, 2], dtype=np.complex128)
        coreTmp[0, :, :, 0] = -0.5j * sY.T
        coreTmp[0, :, :, 1] = np.eye(sZ.shape[0])

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        i = self.ptrBra[1]
        coreTmp = np.zeros([2, 2, 2, 1], dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(sZ.shape[0])
        coreTmp[1, :, :, 0] = 0.5j * sY

        self.H[j, i].bondDimL = coreTmp.shape[0]
        self.H[j, i].bondDimR = coreTmp.shape[3]
        self.H[j, i].level = coreTmp.shape[1]
        self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        # time-independent part
        # reservoir 1 and 2
        j = 0
        for l in range(2):
            coreTmp = np.zeros([6, depth[l]+1, depth[l]+1, 6],
                               dtype=np.complex128)
            for i in range(self.dim[l]):
                k = self.ptrKet[l] + 2 * i + 1
                coreTmp.fill(0)
                coreTmp[0, :, :, 0] = np.eye(depth[l]+1)
                coreTmp[1, :, :, 0] = nu[l][i] * num[l].T
                coreTmp[1, :, :, 1] = np.eye(depth[l]+1)
                coreTmp[1, :, :, 2] = np.sqrt(coeff[l][i]) * ann[l].T
                coreTmp[2, :, :, 2] = np.eye(depth[l]+1)
                coreTmp[3, :, :, 0] = np.sqrt(coeff[l][i]) \
                    * (cre[l].T - ann[l].T)
                coreTmp[3, :, :, 3] = np.eye(depth[l]+1)
                coreTmp[4, :, :, 4] = np.eye(depth[l]+1)
                coreTmp[5, :, :, 5] = np.eye(depth[l]+1)

                self.H[j, k].bondDimL = coreTmp.shape[0]
                self.H[j, k].bondDimR = coreTmp.shape[3]
                self.H[j, k].level = coreTmp.shape[1]
                self.H[j, k].core = copy.deepcopy(coreTmp.flatten(order='F'))

                k = self.ptrKet[l] + 2 * i + 2
                coreTmp.fill(0)
                coreTmp[0, :, :, 0] = np.eye(depth[l]+1)
                coreTmp[1, :, :, 0] = nu[l][i].conj() * num[l].T
                coreTmp[1, :, :, 1] = np.eye(depth[l]+1)
                coreTmp[1, :, :, 2] = np.sqrt(coeff[l][i].conj()) * \
                    (cre[l].T - ann[l].T)
                coreTmp[2, :, :, 2] = np.eye(depth[l]+1)
                coreTmp[3, :, :, 0] = np.sqrt(coeff[l][i].conj()) * ann[l].T
                coreTmp[3, :, :, 3] = np.eye(depth[l]+1)
                coreTmp[4, :, :, 4] = np.eye(depth[l]+1)
                coreTmp[5, :, :, 5] = np.eye(depth[l]+1)

                self.H[j, k].bondDimL = coreTmp.shape[0]
                self.H[j, k].bondDimR = coreTmp.shape[3]
                self.H[j, k].level = coreTmp.shape[1]
                self.H[j, k].core = copy.deepcopy(coreTmp.flatten(order='F'))

        # reservoir 1
        l = 0
        # drive for qubit 1
        coreTmp = np.zeros([2, depth[l]+1, depth[l]+1, 2],
                           dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(depth[l]+1)
        coreTmp[1, :, :, 1] = np.eye(depth[l]+1)

        for j in range(1, 3):
            for i in range(self.ptrKet[l]+1, self.ptrBra[l]):
                self.H[j, i].bondDimL = coreTmp.shape[0]
                self.H[j, i].bondDimR = coreTmp.shape[3]
                self.H[j, i].level = coreTmp.shape[1]
                self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        # drive for qubit 2
        coreTmp = np.zeros([1, depth[l]+1, depth[l]+1, 1],
                           dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(depth[l]+1)

        for j in range(3, 5):
            for i in range(self.ptrKet[l]+1, self.ptrBra[l]):
                self.H[j, i].bondDimL = coreTmp.shape[0]
                self.H[j, i].bondDimR = coreTmp.shape[3]
                self.H[j, i].level = coreTmp.shape[1]
                self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        # reservoir 2
        l = 1
        # drive for qubit 1
        coreTmp = np.zeros([1, depth[l]+1, depth[l]+1, 1],
                           dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(depth[l]+1)

        for j in range(1, 3):
            for i in range(self.ptrKet[l]+1, self.ptrBra[l]):
                self.H[j, i].bondDimL = coreTmp.shape[0]
                self.H[j, i].bondDimR = coreTmp.shape[3]
                self.H[j, i].level = coreTmp.shape[1]
                self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

        # drive for qubit 2
        coreTmp = np.zeros([2, depth[l]+1, depth[l]+1, 2],
                           dtype=np.complex128)
        coreTmp[0, :, :, 0] = np.eye(depth[l]+1)
        coreTmp[1, :, :, 1] = np.eye(depth[l]+1)

        for j in range(3, 5):
            for i in range(self.ptrKet[l]+1, self.ptrBra[l]):
                self.H[j, i].bondDimL = coreTmp.shape[0]
                self.H[j, i].bondDimR = coreTmp.shape[3]
                self.H[j, i].level = coreTmp.shape[1]
                self.H[j, i].core = copy.deepcopy(coreTmp.flatten(order='F'))

    def changeCpl(self, J):
        """change coupling strength between two qubits

            params:
                J (list): list of coupling strength (len(J) = 1)
        """

        sP = np.array([[0.0, 1.0],
                    [0.0, 0.0]], dtype=np.complex128)

        sM = np.array([[0.0, 0.0],
                    [1.0, 0.0]], dtype=np.complex128)

        # ptrKet[0]
        HLocal = self.H[0, self.ptrKet[0]]
        shape4d = (HLocal.bondDimL, HLocal.level, HLocal.level,
                   HLocal.bondDimR)
        coreTmp = copy.deepcopy(HLocal.core.reshape(shape4d, order='F'))

        coreTmp[0, :, :, 4] = -1j * J[0] * sP.T
        coreTmp[0, :, :, 5] = -1j * J[0] * sM.T

        HLocal.core = copy.deepcopy(coreTmp.flatten(order='F'))

        # ptrBra[1]
        HLocal = self.H[0, self.ptrBra[1]]
        shape4d = (HLocal.bondDimL, HLocal.level, HLocal.level,
                   HLocal.bondDimR)
        coreTmp = copy.deepcopy(HLocal.core.reshape(shape4d, order='F'))

        coreTmp[4, :, :, 0] = 1j * J[0] * sM
        coreTmp[5, :, :, 0] = 1j * J[0] * sP

        HLocal.core = copy.deepcopy(coreTmp.flatten(order='F'))

    def changeFreq(self, omegaQ):
        """change qubit frequency

            params:
                omegaQ (list): list of qubit frequency
        """

        sZ = np.array([[1.0,  0.0],
                    [0.0, -1.0]], dtype=np.complex128)

        # ptrKet[0]
        HLocal = self.H[0, self.ptrKet[0]]
        shape4d = (HLocal.bondDimL, HLocal.level, HLocal.level,
                   HLocal.bondDimR)
        coreTmp = copy.deepcopy(HLocal.core.reshape(shape4d, order='F'))

        coreTmp[0, :, :, 0] = -0.5j * omegaQ[0] * sZ.T

        HLocal.core = copy.deepcopy(coreTmp.flatten(order='F'))

        # ptrBra[0]
        HLocal = self.H[0, self.ptrBra[0]]
        shape4d = (HLocal.bondDimL, HLocal.level, HLocal.level,
                   HLocal.bondDimR)
        coreTmp = copy.deepcopy(HLocal.core.reshape(shape4d, order='F'))

        coreTmp[1, :, :, 0] = 0.5j * omegaQ[0] * sZ

        HLocal.core = copy.deepcopy(coreTmp.flatten(order='F'))

        # ptrKet[1]
        HLocal = self.H[0, self.ptrKet[1]]
        shape4d = (HLocal.bondDimL, HLocal.level, HLocal.level,
                   HLocal.bondDimR)
        coreTmp = copy.deepcopy(HLocal.core.reshape(shape4d, order='F'))

        coreTmp[1, :, :, 0] = -0.5j * omegaQ[1] * sZ.T

        HLocal.core = copy.deepcopy(coreTmp.flatten(order='F'))

        # ptrBra[1]
        HLocal = self.H[0, self.ptrBra[1]]
        shape4d = (HLocal.bondDimL, HLocal.level, HLocal.level,
                   HLocal.bondDimR)
        coreTmp = copy.deepcopy(HLocal.core.reshape(shape4d, order='F'))

        coreTmp[1, :, :, 0] = 0.5j * omegaQ[1] * sZ

        HLocal.core = copy.deepcopy(coreTmp.flatten(order='F'))

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
