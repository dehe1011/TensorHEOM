import numpy as np
from .u3 import U3Pulse

class rxyStep(U3Pulse):
    """pulse for single-qubit gates with abrupt change
        elemental gate: U3 gate

        attributes:
            amp (float): amplitude of pulse
            omega (float): drive frequency
            gateTime (float): gate time of RXGate(pi)
            ampSeq (numpy.ndarray): array of amplitude sequence
            phaseSeq (numpy.ndarray): array of phase sequence
    """

    def __init__(self, **kwargs):
        """
            args:
                **kwargs: keyward arguments
                    kwargs['gateTime'] (float): gate time of RXGate(pi)
                    kwargs['omega'] (float): drive frequency
        """

        self.gateTime = kwargs['gateTime']
        self.omega = kwargs['omega']
        self.amp = np.pi / self.gateTime

    def getGateTime(self, dt: float, params: list) -> int:
        """get gate time in the unit of dt
            Note: Use this after vzTransform

            args:
                dt (float): time step for integration of HEOM
                params (list): parameters
                    params[0] (float): rotation angle (theta)
                    
            returns:
                int: gate time
        """

        angle = getAngle(params[0])

        return int(np.abs(angle) / self.amp / dt)
    
    def initSeq(self, totalSize: int) -> None:
        """initialize sequences

            args:
                totalSize (int): total size of the sequence
        """
        
        self.ampSeq = np.zeros(totalSize)
        self.phaseSeq = np.zeros(totalSize)

    def setSeq(self, st: int, dur:int, params: list) -> None:
        """set values for sequences in [st:st+dur]
            Corresponding gate is assumed to be U3(theta, phi, -phi)
            after virtual-Z transformation.

            args:
                st (int): starting point of the pulse
                dur (int): duration of the pulse
                params (list): parameters
                    params[0] (float): theta of U3Gate
                    params[1] (float): phi of U3Gate
        """

        self.ampSeq[st:st+dur] = self.amp
        
        angle = getAngle(params[0])
        phase = params[1] + 0.5*np.pi
        if angle < 0:
            phase += np.pi
        self.phaseSeq[st:st+dur] = phase

    def getPrefactor(self, dt: float, time: float,
                     stepNum: int) -> tuple[float, float]:
        """compute prefactor terms for Runge-Kutta update

            args:
                dt (float): step size for Runge-Kutta integration
                time (float): current time
                stepNum (int): current step number of the integration
            
            returns:
                preSX (float): prefactor for sigma_x term
                preSY (float): prefactor for sigma_y term
        """

        preSX = self.ampSeq[stepNum]\
            * np.cos(self.omega * time + self.phaseSeq[stepNum])
        preSY = self.ampSeq[stepNum]\
            * np.sin(self.omega * time + self.phaseSeq[stepNum])
        
        return preSX, preSY

def getAngle(angle: float) -> float:
    """return a normalized angle in the range (-pi, pi)

        args:
            angle (float): angle

        returns:
            angle (float): normalized angle
    """

    angle = angle % (2 * np.pi)
    if angle > np.pi:
        angle -= 2 * np.pi

    return angle