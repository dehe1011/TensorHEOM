from qiskit.circuit import Instruction, Parameter
from qiskit.circuit.library import U3Gate
from .abstract_pulse import abstractPulse

class U3Pulse(abstractPulse):
    """Single-qubit pulse implemented as a U3 gate with virtual-Z transformation.

    Applies a rotation in the x-y plane combined with a virtual Z gate.
    """

    def elementalGates(self) -> list[Instruction]:
        """Return the elemental gate(s) used for circuit transpilation.

        Returns
        -------
        list of qiskit.circuit.Instruction
            A single-element list containing a parametric U3 gate.
        """
        theta = Parameter('theta')
        phi = Parameter('phi')
        lam = Parameter('lam')

        return [U3Gate(theta, phi, lam)]

    def vzTransform(self, params: list[float], globalPhase: float,
                localPhase: list[float], qubitIdx: list[int])\
        -> tuple[Instruction, float, float]:
        """Apply the virtual-Z transformation to a U3 gate.

        The transformation absorbs Z rotations into the gate phases:

        .. math::

            U_3(\\theta, \\phi, \\lambda)\\, R_Z(a)
            = R_Z(c)\\, U_3(\\theta, -b, b)\\, e^{i\\varphi}

        where :math:`b = \\lambda + a` and :math:`c = a + \\phi + \\lambda`.

        Parameters
        ----------
        params : list of float
            Gate parameters: ``[theta, phi, lam, gate_name]``.
        globalPhase : float
            Accumulated global phase.
        localPhase : list of float
            Per-qubit accumulated local phases (rotation angles of RZ gates).
        qubitIdx : list of int
            Qubit indices to which the gate is applied.

        Returns
        -------
        gateOut : qiskit.circuit.Instruction
            Transformed gate :math:`U_3(\\theta, -b, b)`.
        globalPhase : float
            Updated global phase.
        localPhase : list of float
            Updated per-qubit local phases.
        """

        theta, phi, lam = params[0:3]
        globalPhase += 0.5 * (phi + lam)
        phase = localPhase[qubitIdx[0]]
        gateOut = U3Gate(theta, -(lam + phase), lam+phase)
        localPhase[qubitIdx[0]] += phi + lam

        return gateOut, globalPhase, localPhase

    def isDelayed(self, name: str) -> bool:
        """Return whether an idling period should follow this gate.

        Parameters
        ----------
        name : str
            Gate name (``'u3'``).

        Returns
        -------
        bool
            Always ``True`` for U3 gates.
        """

        return True

    def getEnPtr(self) -> int:
        """Return the index of the last non-zero element in the amplitude sequence.

        Returns
        -------
        int
            End pointer of the active pulse region.
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
        """Trim the pulse sequences to length ``en``.

        Parameters
        ----------
        en : int
            New end index (exclusive).
        """

        self.ampSeq = self.ampSeq[0:en]
        self.phaseSeq = self.phaseSeq[0:en]
