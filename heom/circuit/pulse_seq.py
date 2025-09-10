import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Parameter, Delay, Instruction
from qiskit.transpiler import Target, InstructionProperties
from .transform_circ import transform
from ..TTs import TTs

def setPulseSeq(qc: QuantumCircuit, TTs: TTs, omegaQ: list[float], 
                dtFB: float, idlingTime: float) -> None:
    """compute pulse sequence for HEOM calculation
        Obtained sequences are set to properties in TTs

        params:
            qc (qiskit.QuantumCircuit): quantum circuit to be simulated
            TTs (TTs.TTs): class for MPS and MPO
            dtFB (float): time step for integration of HEOM,
                in the unit of 1/omegaQ[0]
            omegaQ (list[float]): 1d list of qubit frequency
                in the unit of omegaQ[0]
            idlingTime (float): idling time, in the unit of omegaQ[0]
    """

    numQubits = qc.num_qubits

    # create a quantum circuit consisting of elemental gates only
    qcTransformed = transform(qc, TTs)
    
    # apply virtual-Z-gate schemes
    qcVZ = QuantumCircuit(numQubits)
    globalPhase = 0
    localPhase = [0] * numQubits
    for gate in qcTransformed.data:
        params = list(gate.operation.params)
        params.append(gate.operation.name)
        qubitIdx = list(np.sort([q._index for q in gate.qubits]))
        pulseIdx = TTs.map[tuple(qubitIdx)]
        gateOut, globalPhase, localPhase = TTs.pulse[pulseIdx][1].vzTransform(
            params, globalPhase, localPhase, qubitIdx
        )
        qcVZ.append(gateOut, qubitIdx)
    
    qcVZ.global_phase = globalPhase
    TTs.localPhase = localPhase

    # set gate time for each gate and insert idling
    idlingStep = int(idlingTime / dtFB)
    qcWithDelay = QuantumCircuit(numQubits)
    tgt = Target(dt=1)
    deltaT = Parameter('deltaT')
    tgt.add_instruction(Delay(deltaT))

    for i, gate in enumerate(qcVZ.data):
        name = f'g{i}'
        qubitIdx = list(np.sort([q._index for q in gate.qubits]))
        params = gate.operation.params
        pulseIdx = TTs.map[tuple(qubitIdx)]
        dur = TTs.pulse[pulseIdx][1].getGateTime(dtFB, params)
        params = [dur] + params
        
        if len(qubitIdx) == 2:
            gateTmp = Instruction(name, 2, 0, params)
        else:
            gateTmp = Instruction(name, 1, 0, params)

        qcWithDelay.append(gateTmp, qubitIdx)

        if TTs.pulse[pulseIdx][1].isDelayed(gate.operation.name):
            qcWithDelay.delay(idlingStep, qubitIdx)
        

        prop = {tuple(qubitIdx): InstructionProperties(duration=dur)}
        tgt.add_instruction(gateTmp, prop, name)

    qcScheduled = transpile(qcWithDelay, target=tgt, scheduling_method='alap')

    totalSize = qcScheduled.estimate_duration(tgt, 'dt')
    for _, pulse in TTs.pulse:
        pulse.initSeq(totalSize)
    TTs.omegaQSeq = [np.ones(totalSize) * omegaQ[i] for i in range(numQubits)]

    ptr = [0] * numQubits

    for gate in qcScheduled.data:
        if gate.operation.num_qubits == 2:
            qubitIdx = list(np.sort([q._index for q in gate.qubits]))
            pulseIdx = TTs.map[tuple(qubitIdx)]
            dur = gate.operation.params[0]

            st = ptr[qubitIdx[0]]
            omegaQTmp = [omegaQ[qubitIdx[0]], omegaQ[qubitIdx[1]]]
            TTs.omegaQSeq[qubitIdx[0]][st:st+dur], \
                TTs.omegaQSeq[qubitIdx[1]][st:st+dur] = \
                TTs.pulse[pulseIdx][1].setOmegaQ(dur, omegaQTmp)
            
            TTs.pulse[pulseIdx][1].setSeq(ptr[qubitIdx[0]], dur, [])

            ptr[qubitIdx[0]] += dur
            ptr[qubitIdx[1]] += dur
        elif gate.operation.name != 'delay':
            qubitIdx = np.array([gate.qubits[0]._index])
            pulseIdx = TTs.map[tuple(qubitIdx)]
            dur, theta, phi = gate.operation.params[0:3]
            
            TTs.pulse[pulseIdx][1].setSeq(ptr[qubitIdx[0]], dur, [theta, phi])
            ptr[qubitIdx[0]] += dur
        else:
            qubitIdx = gate.qubits[0]._index
            dur = gate.operation.params[0]
            ptr[qubitIdx] += dur

    # crop redundant section at the end of the sequence
    ptrs = []
    for pulse in TTs.pulse:
        ptrs.append(pulse[1].getEnPtr())

    en = max(ptrs)
    for pulse in TTs.pulse:
        pulse[1].cropPulse(en)

    for i in range(numQubits):
        TTs.omegaQSeq[i] = TTs.omegaQSeq[i][0:en]