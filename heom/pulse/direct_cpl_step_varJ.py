import numpy as np
from .iswapd import iSwapDPulse

class directCplStepVarJ(iSwapDPulse):
    """pulse for two-qubit gates with abrupt change
        direct qubit-qubit coupling
        variable coupling strength between qubits

        elemental gate: complex conjugate of iSWAP (iSwapD)
    """

    def __init__(self, **kwargs):
        """
            params:
                **kwargs: keyword arguments
                    kwargs['gateTime'] (float):
                        gate time of XXPlusYYGate(pi) (= iSwapD)
        """
        super().__init__(**kwargs)

        gateTime = kwargs['gateTime']
        self.amp = np.pi / 2 / gateTime

    def getGateTime(self, dt: float, params: list) -> int:
        """get gate time in the unit of dt

            params:
                dt (float): time step for integration of HEOM
                params (list): parameters

            returns:
                int: gate time
        """

        return int(np.pi / 2 / self.amp / dt)
    
    def initSeq(self, totalSize: int) -> None:
        """initialize sequences

            params:
                totalSize (int): total size of the sequence
        """

        self.JSeq = np.zeros(totalSize)

    def setSeq(self, st: int, dur: int, params: list) -> None:
        """set values for sequences in [st:st+dur]

            params:
                st (int): starting point of the pulse
                dur (int): duration of the pulse
                params (list): parameters
        """
        
        self.JSeq[st:st+dur] = self.amp
        
    def setOmegaQ(self, seqSize: int, omegaQ: list[float])\
            -> tuple[np.ndarray, np.ndarray]:
        """return time profiles of qubit frequency

            params:
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

            params:
                dt (float): step size for Runge-Kutta integration
                time (float): current time
                stepNum (int): current step number of the integration
            
            returns:
                preJ (float): prefactor for coupling term
        """

        return self.JSeq[stepNum]
