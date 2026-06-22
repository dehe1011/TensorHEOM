from qiskit.circuit import Instruction, Parameter
from qiskit.circuit.library import U3Gate
from .abstract_pulse import abstractPulse

class U3Pulse(abstractPulse):
    """U3 gate for single-qubit gates
        -> rotation whose angle is in x-y plan + virtual Z gate
    """

    def elementalGates(self) -> list[Instruction]:
        """return a list of elemental gates

            returns (list[qiskit.circuit.Instruction]):
                a list of elemental gates
        """
        theta = Parameter('theta')
        phi = Parameter('phi')
        lam = Parameter('lam')

        return [U3Gate(theta, phi, lam)]

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
                    params[4]: gate name ('u3')
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

        theta, phi, lam = params[0:3]
        globalPhase += 0.5 * (phi + lam)
        phase = localPhase[qubitIdx[0]]
        gateOut = U3Gate(theta, -(lam + phase), lam+phase)
        localPhase[qubitIdx[0]] += phi + lam

        return gateOut, globalPhase, localPhase
    
    def isDelayed(self, name: str) -> bool:
        """returns whether idling should be inserted

            params:
                name (str): gate name ('u3')
            return (bool):
                True: idling is inserted after this gate
                False: idling is not inserted
        """

        return True
       
    def getEnPtr(self) -> int:
        """return end ponit of the pulse sequence

            returns:
                ptr (int): end point of the sequence
        """
        
        length = len(self.ampSeq)
        ptr = length - 1
        for i in range(length-1, -1, -1):
            if self.ampSeq[ptr] == 0.0:
                ptr -= 1
                continue
            else:
                ptr += 1
                break

        return ptr
    
    def cropPulse(self, en) -> None:
        """crop the sequence

            params:
                en (int): end point of the sequence
        """

        self.ampSeq = self.ampSeq[0:en]
        self.phaseSeq = self.phaseSeq[0:en]    