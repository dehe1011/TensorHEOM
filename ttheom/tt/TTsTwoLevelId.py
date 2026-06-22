import numpy as np
from .TTs import TTs

class TTsTwoLevelId(TTs):
    """class for two-level systems (independent reservoir)

        attributes:
            sysEye (numpy.ndarray): identity operator for the system
            shape1QKet (tuple): shape of MPO core for single-qubit operator
                acting on ket vector
            shape1QBra (tuple): shape of MPO core for single-qubit operator
                acting on bra vector
            coreKetSX/Y/Z (numpy.ndarray): MPO core for sigma_X/Y/Z
                acting on ket vector
            coreBraSX/Y/Z (numpy.ndarray): MPO core for sigma_X/Y/Z
                acting on bra vector

            shapeJKet1 (tuple): shape of MPO core for two-qubit operator
                acting on ket vector for one of the coupled qubit
            shapeJKet2 (tuple): shape of MPO core for two-qubit operator
                acting on ket vector for the other copuled qubit
            shapeJBra1 (tuple): shape of MPO core for two-qubit operator
                acting on bra vector for one of the coupled qubit
            shapeJBra2 (tuple): shape of MPO core for two-qubit operator
                acting on bra vector for the other copuled qubit
            coreJKet1 (numpy.ndarray): MPO core for direct coupling 
                acting on ket vector for one of the coupled qubit
            coreJKet2 (numpy.ndarray): MPO core for direct coupling 
                acting on ket vector for the other coupled qubit
            coreJBra1 (numpy.ndarray): MPO core for direct coupling 
                acting on bra vector for one of the coupled qubit
            coreJBra2 (numpy.ndarray): MPO core for direct coupling 
                acting on bra vector for the other coupled qubit

            shapeSysEye1 (tuple): shape of MPO core for identity operator
                acting on ket/bra vectors of system
                bond dimension = 1
            coreSysEye1 (numpy.ndarray): MPO core for identity operator
                acting on ket/bra vectors of system
                bond dimension = 1
    """

    def __init__(self, depth):
        """args:
            depth (list):
                1d list of depth of hierarchy of FP-HEOM (from 0 to depth)
        """

        super().__init__(depth)

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
        
        self.sysEye = np.eye(sZ.shape[0])

        self.shapeKet = (1, 2, 2, 2)

        coreTmp = np.zeros(self.shapeKet, dtype=np.complex128)
        coreTmp[0, :, :, 1] = self.sysEye
        
        coreTmp[0, :, :, 0] =  0.5j * sZ.T
        self.coreKetSZ = coreTmp.flatten(order='F')

        coreTmp[0, :, :, 0] =  -0.5j * sX.T
        self.coreKetSX = coreTmp.flatten(order='F')

        coreTmp[0, :, :, 0] =  -0.5j * sY.T
        self.coreKetSY = coreTmp.flatten(order='F')

        self.shapeBra = (2, 2, 2, 1)

        coreTmp = np.zeros(self.shapeBra, dtype=np.complex128)
        coreTmp[0, :, :, 0] = self.sysEye
        
        coreTmp[1, :, :, 0] = -0.5j * sZ
        self.coreBraSZ = coreTmp.flatten(order='F')

        coreTmp[1, :, :, 0] = 0.5j * sX
        self.coreBraSX = coreTmp.flatten(order='F')

        coreTmp[1, :, :, 0] = 0.5j * sY
        self.coreBraSY = coreTmp.flatten(order='F')

        self.shapeJKet1 = (1, 2, 2, 3)
        coreTmp = np.zeros(self.shapeJKet1, dtype=np.complex128)
        coreTmp[0, :, :, 0] = self.sysEye
        coreTmp[0, :, :, 1] = -1j * sP.T
        coreTmp[0, :, :, 2] = -1j * sM.T
        self.coreJKet1 = coreTmp.flatten(order='F')

        self.shapeJBra1 = (3, 2, 2, 4)
        coreTmp = np.zeros(self.shapeJBra1, dtype=np.complex128)
        coreTmp[0, :, :, 2] = sP
        coreTmp[0, :, :, 3] = sM
        coreTmp[1, :, :, 0] = self.sysEye
        coreTmp[2, :, :, 1] = self.sysEye
        self.coreJBra1 = coreTmp.flatten(order='F')

        self.shapeJKet2 = (4, 2, 2, 3)
        coreTmp = np.zeros(self.shapeJKet2, dtype=np.complex128)
        coreTmp[0, :, :, 0] = sM.T
        coreTmp[1, :, :, 0] = sP.T
        coreTmp[2, :, :, 1] = self.sysEye
        coreTmp[3, :, :, 2] = self.sysEye
        self.coreJKet2 = coreTmp.flatten(order='F')

        self.shapeJBra2 = (3, 2, 2, 1)
        coreTmp = np.zeros(self.shapeJBra2, dtype=np.complex128)
        coreTmp[0, :, :, 0] = self.sysEye
        coreTmp[1, :, :, 0] = 1j * sM
        coreTmp[2, :, :, 0] = 1j * sP
        self.coreJBra2 = coreTmp.flatten(order='F')

        self.shapeSysEye1 = (1, 2, 2, 1)
        coreTmp = np.zeros(self.shapeSysEye1, dtype=np.complex128)
        coreTmp[0, :, :, 0] = self.sysEye
        self.coreSysEye1 = coreTmp.flatten(order='F')

    def getRDO(self):
        """compute reduced density matrix

            returns:
                rhoOut (numpy.ndarray): reduced density matrix,
                    1D array in row-major order
        """

        i = 0
        rhoTmp = np.eye(1)

        for j in range(self.numQ):
            i = self.ptrKet[j]
            coreTmp = self.rho[i].core.reshape([self.rho[i].bondDimL, -1],
                                               order='F')
            rhoTmp = rhoTmp @ coreTmp
            rhoTmp = rhoTmp.reshape([-1, self.rho[i].bondDimR], order='F')

            for i in range(self.ptrKet[j]+1, self.ptrBra[j]):
                coreTmp = self.rho[i].core.reshape(
                    [self.rho[i].bondDimL,
                     self.rho[i].level,
                     self.rho[i].bondDimR],
                    order='F')
                rhoTmp = rhoTmp @ coreTmp[:, 0, :]
                rhoTmp = rhoTmp.reshape([-1, self.rho[i].bondDimR], order='F')

            i = self.ptrBra[j]
            coreTmp = self.rho[i].core.reshape([self.rho[i].bondDimL, -1],
                                               order='F')
            rhoTmp = rhoTmp @ coreTmp
            rhoTmp = rhoTmp.reshape([-1, self.rho[i].bondDimR], order='F')

        rhoSize = 4**self.numQ
        rhoOut = np.zeros(rhoSize, dtype=np.complex128)

        formatSpec = f'0{2*self.numQ}b'        
        for i in range(rhoSize):
            indexTmp = format(i, formatSpec)
            index = indexTmp[-1::-2] + indexTmp[-2::-2]
            rhoOut[int(index, 2)] = rhoTmp[i]

        rhoOut = rhoOut.reshape([2**self.numQ, 2**self.numQ])
        return rhoOut