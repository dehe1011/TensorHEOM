import numpy as np
from .iswapd import iSwapDPulse

class directCplStepVarJ(iSwapDPulse):
    """Two-qubit pulse with abrupt (step-function) coupling strength changes.

    Implements direct qubit-qubit coupling with a variable coupling strength,
    using the iSWAP-dagger gate as the elemental two-qubit operation.

    Attributes
    ----------
    amp : float
        Pulse amplitude (rad per time unit).
    gateTime : float
        Gate time of the :math:`XX+YY(\\pi)` (= iSWAP-dagger) operation.
    JSeq : numpy.ndarray
        Time sequence of coupling strengths between qubits.
    """

    def __init__(self, **kwargs):
        """Initialize the pulse from keyword arguments.

        Parameters
        ----------
        **kwargs
            Keyword arguments.

            ``gateTime`` : float
                Gate time of the :math:`XX+YY(\\pi)` (= iSWAP-dagger) operation.
        """
        super().__init__(**kwargs)

        self.gateTime = kwargs['gateTime']
        self.amp = np.pi / 2 / self.gateTime

    def getGateTime(self, dt: float, params: list) -> int:
        """Return the gate duration in units of ``dt``.

        Parameters
        ----------
        dt : float
            Time step for HEOM integration.
        params : list
            Gate parameters (unused for this gate type).

        Returns
        -------
        int
            Gate duration (number of time steps).
        """

        return int(np.pi / 2 / self.amp / dt)

    def initSeq(self, totalSize: int) -> None:
        """Allocate and zero-initialize the coupling-strength sequence.

        Parameters
        ----------
        totalSize : int
            Total number of time steps.
        """

        self.JSeq = np.zeros(totalSize)

    def setSeq(self, st: int, dur: int, params: list) -> None:
        """Set the coupling-strength sequence in the interval ``[st, st+dur)``.

        Parameters
        ----------
        st : int
            Starting time step.
        dur : int
            Duration in time steps.
        params : list
            Gate parameters (unused for this gate type).
        """

        self.JSeq[st:st+dur] = self.amp

    def setOmegaQ(self, seqSize: int, omegaQ: list[float])\
            -> tuple[np.ndarray, np.ndarray]:
        """Return the qubit-frequency profiles during the two-qubit gate.

        Both qubits are tuned to the lower of the two qubit frequencies.

        Parameters
        ----------
        seqSize : int
            Number of time steps.
        omegaQ : list of float
            Qubit frequencies of the two involved qubits.

        Returns
        -------
        omegaQSeq0 : numpy.ndarray
            Frequency profile of the first qubit.
        omegaQSeq1 : numpy.ndarray
            Frequency profile of the second qubit.
        """

        omegaTmp = min(omegaQ)

        omegaQSeq0 = np.zeros(seqSize)
        omegaQSeq1 = np.zeros(seqSize)

        omegaQSeq0[:] = omegaTmp
        omegaQSeq1[:] = omegaTmp

        return omegaQSeq0, omegaQSeq1

    def getPrefactor(self, dt: float, time, stepNum) -> float:
        """Compute the coupling prefactor for the Runge-Kutta update.

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
        float
            Prefactor for the qubit-qubit coupling term.
        """

        return self.JSeq[stepNum]

    def getEnPtr(self) -> int:
        """Return the index of the last non-zero element in the coupling sequence.

        Returns
        -------
        int
            End pointer of the active pulse region.
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
        """Trim the coupling sequence to length ``en``.

        Parameters
        ----------
        en : int
            New end index (exclusive).
        """

        self.JSeq = self.JSeq[0:en]
