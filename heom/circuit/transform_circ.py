from numpy import pi
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import Target
from qiskit.circuit import Delay, Parameter
from ..tt.TTs import TTs

def transform(qc: QuantumCircuit, TTs: TTs):
    """transform a quantum circuit into a circuit consisting of
        'rx', 'ry', and 'xx_plus_yy' 

        args:
            qc (qiskit.QuantumCircuit): 
                quantum circuit to be transformed
            TTs (TTs): class for MPS and MPO

        returns:
            qiskit.QuantumCircuit: quantum circuit consisting of 
                elemental gates defined in TTs
    """

    propDict = {}
    for qubitIdx, pulse in TTs.pulse:
        if len(qubitIdx) == 1:
            prop = {tuple(qubitIdx): None}
        else:
            prop = {tuple(qubitIdx): None,
                    (qubitIdx[1], qubitIdx[0]): None}

        for eGate in pulse.elementalGates():
            name = eGate.name
            if name not in propDict.keys():
                propDict[name] = prop
            else:
                for k, v in prop.items():
                    propDict[name][k] = v

    isAdded = {}
    for k in propDict.keys():
        isAdded[k] = False

    tgt = Target()

    numQubit = qc.num_qubits
    dur = Parameter('dur')
    for i in range (numQubit):
        propDelay = {(i, ): None}
    tgt.add_instruction(Delay(dur), propDelay)

    for _, pulse in TTs.pulse:
        for eGate in pulse.elementalGates():
            key = eGate.name
            if not isAdded[key]:
                tgt.add_instruction(eGate, propDict[key])
                isAdded[key] = True

    return transpile(qc, target=tgt, optimization_level=1)

def scheduling(qc:QuantumCircuit):
    """padding delay for synchronization
        scheduling method: ALAP

        args:
            qc (qiskit.QuantumCircuit): 
                quantum circuit to be transformed

        returns:
            qcNew (qiskit.QuantumCircuit):
                quantum circuit with delay
    """

    # align in reverse order for ALAP
    lastTimes = [0] * qc.num_qubits
    qcReverse = QuantumCircuit(qc.num_qubits)

    for ope, qargs, cargs in reversed(qc.data):
        qubitIdx = [q._index for q in qargs]

        startTime = max([lastTimes[q] for q in qubitIdx])
        for q in qubitIdx:
            timeDiff = startTime - lastTimes[q]
            if timeDiff > 0:
                qcReverse.delay(timeDiff, q)

        qcReverse.append(ope, qubitIdx)

        dur = int(ope.params[0])
        for q in qubitIdx:
            lastTimes[q] = startTime + dur

    timeMax = max(lastTimes)
    for q in range(qc.num_qubits):
        timeDiff = timeMax - lastTimes[q]
        if timeDiff > 0:
            qcReverse.delay(timeDiff, q)

    # align in original order
    qcNew = QuantumCircuit(qc.num_qubits)
    for ope, qargs, cargs in reversed(qcReverse.data):
        qubitIdx = [q._index for q in qargs]

        qcNew.append(ope, qubitIdx)

    return qcNew