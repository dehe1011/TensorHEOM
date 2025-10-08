import numpy as np
from .TTs import TTs

class TTsTwoLevel(TTs):
    """class for two-level systems

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
    """

    def __init__(self, depth):
        """params:
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


