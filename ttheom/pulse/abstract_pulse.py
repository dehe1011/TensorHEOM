from abc import ABC, abstractmethod
from qiskit.circuit import Instruction

class abstractPulse(ABC):
    """Abstract base class for pulse shapes.

    Pulse shape and associated quantities are represented as
    discretized time sequences.
    """
    def __init__(self, **kwargs):
        """Initialize pulse parameters from keyword arguments."""
        pass

    @abstractmethod
    def getGateTime(self, dt: float, params: list) -> int:
        """Return the gate duration in units of ``dt``.

        Parameters
        ----------
        dt : float
            Integration time step.
        params : list
            Gate parameters.

        Returns
        -------
        int
            Gate duration (number of time steps).
        """

    @abstractmethod
    def initSeq(self, totalSize: int) -> None:
        """Allocate and zero-initialize the pulse sequences.

        Parameters
        ----------
        totalSize : int
            Total number of time steps.
        """

    @abstractmethod
    def setSeq(self, st: int, dur: int, params: list) -> None:
        """Fill the pulse sequences for the interval ``[st, st+dur)``.

        Parameters
        ----------
        st : int
            Starting time step.
        dur : int
            Duration in time steps.
        params : list
            Gate parameters used to compute the pulse shape.
        """

    @abstractmethod
    def getPrefactor(self, dt: float, time: float,
                     stepNum: int):
        """Compute the Hamiltonian prefactors for the Runge-Kutta update.

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
        tuple
            Prefactor values (type and count depend on the concrete subclass).
        """

    @abstractmethod
    def elementalGates(self) -> list[Instruction]:
        """Return the list of elemental gate instructions for circuit transpilation.

        Returns
        -------
        list of qiskit.circuit.Instruction
            Elemental gate instructions supported by this pulse.
        """

    @abstractmethod
    def vzTransform(self, params, globalPhase, localPhase, qubtIdx)\
        -> tuple[Instruction, float, list[float]]:
        """Apply a virtual-Z transformation to gate parameters.

        Parameters
        ----------
        params : list
            Gate parameters before transformation.
        globalPhase : float
            Accumulated global phase.
        localPhase : list of float
            Per-qubit accumulated local phases.
        qubtIdx : list of int
            Qubit indices involved in this gate.

        Returns
        -------
        gate : qiskit.circuit.Instruction
            Transformed gate instruction.
        globalPhase : float
            Updated global phase.
        localPhase : list of float
            Updated per-qubit local phases.
        """

    @abstractmethod
    def isDelayed(self, name) -> bool:
        """Return whether the named gate is treated as a delay.

        Parameters
        ----------
        name : str
            Gate name.

        Returns
        -------
        bool
            ``True`` if the gate is a delay, ``False`` otherwise.
        """

    @abstractmethod
    def getEnPtr(self) -> int:
        """Return the index of the last non-zero element in the pulse sequence.

        Returns
        -------
        int
            End pointer of the active pulse region.
        """

    @abstractmethod
    def cropPulse(self, en) -> None:
        """Trim the pulse sequences to length ``en``.

        Parameters
        ----------
        en : int
            New end index (exclusive) for all pulse sequence arrays.
        """
