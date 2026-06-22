import numpy as np
from .iswapd import iSwapDPulse

class directCplStepVarJ(iSwapDPulse):
    """pulse for two-qubit gates with abrupt change
        direct qubit-qubit coupling
        variable coupling strength between qubits

        elemental gate: complex conjugate of iSWAP (iSwapD)

        attributes:
            amp (float): amplitude of pulse
            gateTime (float): gate time of XXPlusYYGate(pi) (= iSwapD)
            JSeq (numpy.ndarray):
                sequence of coupling strength between qubits
    """

    def __init__(self, **kwargs):
        """
            args:
                **kwargs: keyword arguments
                    kwargs['gateTime'] (float):
                        gate time of XXPlusYYGate(pi) (= iSwapD)
        """
        super().__init__(**kwargs)

        self.gateTime = kwargs['gateTime']
        self.amp = np.pi / 2 / self.gateTime

    def getGateTime(self, dt: float, params: list) -> int:
        """get gate time in the unit of dt

            args:
                dt (float): time step for integration of HEOM
                params (list): parameters

            returns:
                int: gate time
        """

        return int(np.pi / 2 / self.amp / dt)
    
    def initSeq(self, totalSize: int) -> None:
        """initialize sequences

            args:
                totalSize (int): total size of the sequence
        """

        self.JSeq = np.zeros(totalSize)

    def setSeq(self, st: int, dur: int, params: list) -> None:
        """set values for sequences in [st:st+dur]

            args:
                st (int): starting point of the pulse
                dur (int): duration of the pulse
                params (list): parameters
        """
        
        self.JSeq[st:st+dur] = self.amp
        
    def setOmegaQ(self, seqSize: int, omegaQ: list[float])\
            -> tuple[np.ndarray, np.ndarray]:
        """return time profiles of qubit frequency

            args:
                seqSize (int): sequence size
                omegaQ (list): 1d list of qubit frequency

            returns:
                omegaQSeq0 (numpy.ndarray): 1d array for
                    time profile of qubit frequency of the first qubit
                omegaQSeq1 (numpy.ndarray): 1d array for
                    time profile of qubit frequency of the second qubit
        """

        omegaTmp = min(omegaQ)

        omegaQSeq0 = np.zeros(seqSize)
        omegaQSeq1 = np.zeros(seqSize)

        omegaQSeq0[:] = omegaTmp
        omegaQSeq1[:] = omegaTmp

        return omegaQSeq0, omegaQSeq1

    def getPrefactor(self, dt: float, time, stepNum) -> float:
        """compute prefactor terms for Runge-Kutta update

            args:
                dt (float): step size for Runge-Kutta integration
                time (float): current time
                stepNum (int): current step number of the integration
            
            returns:
                preJ (float): prefactor for coupling term
        """

        return self.JSeq[stepNum]

    def getEnPtr(self) -> int:
        """return end ponit of the pulse
        """
        
        length = len(self.JSeq)
        ptr = length - 1
        for i in range(length-1, -1, -1):
            if self.JSeq[ptr] == 0.0:
                ptr -= 1
                continue
            else:
                ptr += 1
                break

        return ptr
    
    def cropPulse(self, en) -> None:
        """crop the sequence

            args:
                en (int): end point of the sequence
        """

        self.JSeq = self.JSeq[0:en]    