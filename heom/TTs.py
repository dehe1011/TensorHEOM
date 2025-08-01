from abc import ABC, abstractmethod

class TTs(ABC):
    """abstract class for MPS and MPO

        attributes:
            numCore (int): number of cores
            dim (list): list of dimension of reservoir mode
            ptrKet, ptrBra (list): list of pointer to ket/bra vector of spin
            rho (numpy.ndarray): 1d array of tt.zTT (MPS)
            H (numpy.ndarray): 2d array of tt.zTT (MPO)
            indices (numpy.ndarray): 2d array of MPS indices
    """

    def __init__(self):
        self.numCore = None
        self.dim = None
        self.ptrKet = None
        self.ptrBra = None
        self.rho = None
        self.H = None
        self.indices = None

    @abstractmethod
    def changeFreq(self, omegaQ):
        pass

    @abstractmethod
    def changeCpl(self, J):
        pass
