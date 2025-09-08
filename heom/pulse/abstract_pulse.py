from abc import ABC, abstractmethod
from qiskit.circuit import Instruction

class abstractPulse(ABC):
    """abstract class for pulse shape
        Pulse shape and associated quantities are given in
        discretized time sequences.
    """
    def __init__(self, **kwargs):
        """ If necessary, add decomposition of gate here.
        """
        pass

    @abstractmethod
    def getGateTime(self, dt: float, params: list) -> int:
        pass

    @abstractmethod
    def initSeq(self, totalSize: int) -> None:
        pass

    @abstractmethod
    def setSeq(self, st: int, dur:int, params: list) -> None:
        pass

    @abstractmethod
    def getPrefactor(self, dt: float, time: float, 
                     stepNum: int):
        pass

    @abstractmethod
    def elementalGates(self) -> list[Instruction]:
        pass

    @abstractmethod
    def vzTransform(self, params, globalPhase, localPhase, qubtIdx)\
        -> tuple[Instruction, float, list[float]]:
        pass

    @abstractmethod
    def isDelayed(self, name) -> bool:
        pass