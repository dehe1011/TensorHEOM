from abc import ABC, abstractmethod

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

    @abstractmethod
    def getPrefactors(self, dt: float, time: float, stepNum: int):
        pass