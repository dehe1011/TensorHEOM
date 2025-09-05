from qiskit.circuit import Instruction, Parameter
from qiskit.circuit.library import U3Gate
from .abstract_pulse import abstractPulse

class U3Pulse(abstractPulse):
    """U3 gate for single-qubit gates
        -> rotation whose angle is in x-y plan + virtual Z gate
    """

    def elementalGate(self) -> Instruction:
        """return elemental gate

            returns (qiskit.circuit.Instruction):
                elemental gate
        """
        theta = Parameter('theta')
        phi = Parameter('phi')
        lam = Parameter('lam')

        return U3Gate(theta, phi, lam)

    def vzTransform(self, params: list[float], globalPhase: float,
                localPhase: list[float], qubitIdx: list[int])\
        -> tuple[Instruction, float, float]:
        """transform U3 gate by utilizing the virtual Z gate
            U3Gate(theta, phi, lam) RZGate(a)
                = RZGate(c) U3Gate(theta, -b, b) * exp(1j*globalPhase)
                b = lam + a
                c = a + phi + lam

            params:
                params (list[float]): parameters
                    params[0]: theta
                    params[1]: phi
                    params[2]: lam
                    for U3Gate(theta, phi, lam)
                globalPhase (float): global phase
                localPhase (list[float]): rotation angle of RZGate
                    before U3Gate
                qubitIdx (list[int]): qubit indeces 
                    to which the gate is applied

            returns:
                gateOut (qiskit.circuit.Instruction):
                    new gate, U3(theta, -k, k)
                globalPhase (float): updated global phase
                localPhase (float): rotation angle of RZGate
                    after the new U3Gate
        """

        theta, phi, lam = params
        globalPhase += 0.5 * (phi + lam)
        phase = localPhase[qubitIdx[0]]
        gateOut = U3Gate(theta, -(lam + phase), lam+phase)
        localPhase[qubitIdx[0]] += phi + lam

        return gateOut, globalPhase, localPhase