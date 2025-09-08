import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Instruction
from qiskit.circuit.library import XXPlusYYGate, CXGate, iSwapGate
from .abstract_pulse import abstractPulse

class iSwapDPulse(abstractPulse):
    """complex conjugate of iSwap gate (iSwap-dagger, iSwapD)

        attributes:
            iSwapD (qiskit.circuit.Instruction): iSwapD gate
            iSwapDSkip (qiskit.circiut.instruction): iSwapD gate
                without idling
    """

    def __init__(self):

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
        """return a list of elemental gate

            returns (list[qiskit.circuit.Instruction]):
                a list of elemental gates
        """

        return [self.iSwapD(), self.iSwapDSkip()]

    def vzTransform(self, params: list, globalPhase: float,
                    localPhase: list[float], qubitIdx: list[int])\
        -> tuple[Instruction, float, list[float]]:
        """transform iSwapD by utilizing the virtual Z gate

            params:
                params (list): parameters
                    params[0]: gate name ('iswapd' or 'iswapdskip') 
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

        if params[0] == 'iswapd':
            gateOut = self.iSwapD()
        else:
            gateOut = self.iSwapDSkip()

        return gateOut, globalPhase, localPhase
    
    def isDelayed(self, name: str) -> bool:
        """returns whether idling should be inserted

            params:
                name (str): gate name ('iswapd' or 'iswapdskip')
            return (bool):
                True: idling is inserted after this gate
                False: idling is not inserted
        """

        return True if name == 'iswapd' else False