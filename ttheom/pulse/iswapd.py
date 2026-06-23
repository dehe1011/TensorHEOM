import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Instruction
from qiskit.circuit.library import XXPlusYYGate, CXGate, iSwapGate
from .abstract_pulse import abstractPulse

class iSwapDPulse(abstractPulse):
    """Pulse implementation for the iSWAP-dagger (complex conjugate of iSWAP) gate.

    Attributes
    ----------
    iSwapD : qiskit.circuit.Gate
        The iSWAP-dagger gate (with idling).
    iSwapDSkip : qiskit.circuit.Gate
        The iSWAP-dagger gate (without idling).
    """

    def __init__(self, **kwargs):

        # create iSwapD gate
        qc = QuantumCircuit(2, name='iswapd')
        qc.append(XXPlusYYGate(np.pi, 0), [0, 1])

        self.iSwapD = qc.to_gate

        qc = QuantumCircuit(2, name='iswapdskip')
        qc.append(XXPlusYYGate(np.pi, 0), [0, 1])

        self.iSwapDSkip = qc.to_gate

        # add decomposition
        qc = QuantumCircuit(2)
        qc.rx(0.5*np.pi, 1)
        qc.append(self.iSwapD(), [0, 1])
        qc.ry(0.5*np.pi, 0)
        qc.append((self.iSwapD()), [0, 1])
        qc.rz(-0.5*np.pi, 0)
        qc.rz(np.pi, 1)
        qc.global_phase = 0.25*np.pi

        CXGate().add_decomposition(qc)

        qc = QuantumCircuit(2)
        qc.append(self.iSwapDSkip(), [0, 1])
        qc.append(self.iSwapDSkip(), [0, 1])
        qc.append(self.iSwapD(), [0, 1])

        iSwapGate().add_decomposition(qc)

    def elementalGates(self) -> list[Instruction]:
        """Return the list of elemental gate instructions.

        Returns
        -------
        list of qiskit.circuit.Instruction
            ``[iSwapD, iSwapDSkip]``.
        """

        return [self.iSwapD(), self.iSwapDSkip()]

    def vzTransform(self, params: list, globalPhase: float,
                    localPhase: list[float], qubitIdx: list[int])\
        -> tuple[Instruction, float, list[float]]:
        """Apply the virtual-Z transformation to an iSWAP-dagger gate.

        The iSWAP-dagger gate swaps the local Z phases of the two qubits.

        Parameters
        ----------
        params : list
            Gate parameters; ``params[0]`` is the gate name
            (``'iswapd'`` or ``'iswapdskip'``).
        globalPhase : float
            Accumulated global phase (unchanged by this gate).
        localPhase : list of float
            Per-qubit accumulated local phases; the phases of the two
            involved qubits are swapped.
        qubitIdx : list of int
            Qubit indices to which the gate is applied.

        Returns
        -------
        gateOut : qiskit.circuit.Instruction
            The iSWAP-dagger gate instruction.
        globalPhase : float
            Unchanged global phase.
        localPhase : list of float
            Updated per-qubit local phases (two entries swapped).
        """

        phaseTmp = localPhase[qubitIdx[0]]
        localPhase[qubitIdx[0]] = localPhase[qubitIdx[1]]
        localPhase[qubitIdx[1]] = phaseTmp

        if params[0] == 'iswapd':
            gateOut = self.iSwapD()
        else:
            gateOut = self.iSwapDSkip()

        return gateOut, globalPhase, localPhase

    def isDelayed(self, name: str) -> bool:
        """Return whether an idling period should follow this gate.

        Parameters
        ----------
        name : str
            Gate name (``'iswapd'`` or ``'iswapdskip'``).

        Returns
        -------
        bool
            ``True`` for ``'iswapd'``, ``False`` for ``'iswapdskip'``.
        """

        return True if name == 'iswapd' else False
