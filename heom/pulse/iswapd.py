import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Instruction
from qiskit.circuit.library import XXPlusYYGate, CXGate, iSwapGate
from .abstract_pulse import abstractPulse

class iSwapDPulse(abstractPulse):
    """complex conjugate of iSwap gate (iSwap-dagger, iSwapD)

        attributes:
            iSwapD (qiskit.circuit.Instruction): iSwapD gate
    """

    def __init__(self):

        # create iSwapD gate
        qc = QuantumCircuit(2, name='iswapd')
        qc.append(XXPlusYYGate(np.pi, 0), [0, 1])

        self.iSwapD = qc.to_gate

        # add decomposition
        qc = QuantumCircuit(2)
        qc.rx(0.5*np.pi, 1)
        qc.append(self.iSwapD(), [0, 1])
        qc.ry(0.5*np.pi, 0)
        qc.append(self.iSwapD(), [0, 1])
        qc.rz(-0.5*np.pi, 0)
        qc.rz(np.pi, 1)
        qc.global_phase = 0.25*np.pi

        CXGate().add_decomposition(qc)

        qc = QuantumCircuit(2)
        qc.append(self.iSwapD(), [0, 1])
        qc.append(self.iSwapD(), [0, 1])
        qc.append(self.iSwapD(), [0, 1])

        iSwapGate().add_decomposition(qc)

    def elementalGate(self) -> Instruction:
        """return elemental gate

            returns (qiskit.circuit.Instruction):
                elemental gate
        """

        return self.iSwapD()

    def vzTransform(self, params: list, globalPhase: float,
                    localPhase: list[float], qubitIdx: list[int])\
        -> tuple[Instruction, float, list[float]]:
        """transform iSwapD by utilizing the virtual Z gate

            params:
                params (list): parameters
                globalPhase (float): global phase
                localPhase (list[float]): rotation angle of RZGate
                    before iSwapD
                qubitIdx (list[int]): qubit indeces
                    to which the gate is applied

            returns:
                gateOut (qiskit.circuit.Instruction):
                    new gate
                globalPhase (float): updated global phase
                localPhase (list[float]): rotation angle of RZGate
                    after iSwapD gate        
        """

        phaseTmp = localPhase[qubitIdx[0]]
        localPhase[qubitIdx[0]] = localPhase[qubitIdx[1]]
        localPhase[qubitIdx[1]] = phaseTmp

        gateOut = self.iSwapD()

        return gateOut, globalPhase, localPhase