import numpy as np
from .u3 import U3Pulse

class rxyStep(U3Pulse):
    """Single-qubit pulse with abrupt (step-function) amplitude changes.

    Implements the :class:`~ttheom.pulse.abstract_pulse.abstractPulse`
    interface using a U3-gate decomposition.

    Attributes
    ----------
    amp : float
        Pulse amplitude (rad per time unit).
    omega : float
        Drive frequency (rad per time unit).
    gateTime : float
        Gate time for an :math:`R_x(\\pi)` rotation.
    ampSeq : numpy.ndarray
        Time sequence of pulse amplitudes.
    phaseSeq : numpy.ndarray
        Time sequence of pulse phases.
    """

    def __init__(self, **kwargs):
        """Initialize the pulse from keyword arguments.

        Parameters
        ----------
        **kwargs
            Keyword arguments.

            ``gateTime`` : float
                Gate time for an :math:`R_x(\\pi)` rotation.
            ``omega`` : float
                Drive frequency.
        """

        self.gateTime = kwargs['gateTime']
        self.omega = kwargs['omega']
        self.amp = np.pi / self.gateTime

    def getGateTime(self, dt: float, params: list) -> int:
        """Return the gate duration in units of ``dt``.

        .. note::
            Call this method only after :meth:`vzTransform` has been applied.

        Parameters
        ----------
        dt : float
            Time step for HEOM integration.
        params : list
            Gate parameters; ``params[0]`` is the rotation angle theta.

        Returns
        -------
        int
            Gate duration (number of time steps).
        """

        angle = getAngle(params[0])

        return int(np.abs(angle) / self.amp / dt)

    def initSeq(self, totalSize: int) -> None:
        """Allocate and zero-initialize the amplitude and phase sequences.

        Parameters
        ----------
        totalSize : int
            Total number of time steps.
        """

        self.ampSeq = np.zeros(totalSize)
        self.phaseSeq = np.zeros(totalSize)

    def setSeq(self, st: int, dur: int, params: list) -> None:
        """Set pulse values in the interval ``[st, st+dur)``.

        The corresponding gate is assumed to be :math:`U_3(\\theta, \\phi, -\\phi)`
        after virtual-Z transformation.

        Parameters
        ----------
        st : int
            Starting time step.
        dur : int
            Duration in time steps.
        params : list
            Gate parameters; ``params[0]`` is theta and ``params[1]`` is phi
            of the U3 gate.
        """

        self.ampSeq[st:st+dur] = self.amp

        angle = getAngle(params[0])
        phase = params[1] + 0.5*np.pi
        if angle < 0:
            phase += np.pi
        self.phaseSeq[st:st+dur] = phase

    def getPrefactor(self, dt: float, time: float,
                     stepNum: int) -> tuple[float, float]:
        """Compute the :math:`\\sigma_x` and :math:`\\sigma_y` prefactors.

        Parameters
        ----------
        dt : float
            Integration time step.
        time : float
            Current time.
        stepNum : int
            Current step number.

        Returns
        -------
        preSX : float
            Prefactor for the :math:`\\sigma_x` term.
        preSY : float
            Prefactor for the :math:`\\sigma_y` term.
        """

        preSX = self.ampSeq[stepNum]\
            * np.cos(self.omega * time + self.phaseSeq[stepNum])
        preSY = self.ampSeq[stepNum]\
            * np.sin(self.omega * time + self.phaseSeq[stepNum])

        return preSX, preSY

def getAngle(angle: float) -> float:
    """Normalize an angle to the range :math:`(-\\pi, \\pi]`.

    Parameters
    ----------
    angle : float
        Input angle in radians.

    Returns
    -------
    float
        Normalized angle in :math:`(-\\pi, \\pi]`.
    """

    angle = angle % (2 * np.pi)
    if angle > np.pi:
        angle -= 2 * np.pi

    return angle
