import numpy as np
from scipy.integrate import simpson
from .tt.TTs import TTs
from .tdevott import timeEvolution

def calcDynamics(dtFB: float, stride: int,
                 TTs: TTs, timeEvo: timeEvolution, file):
    """conduct calculation according to params
    
        params:
            dtFB (float): step width for forward + backward time integration
            stride (int): loops per output
            TTs (TTs.TTs): MPS and MPO
                MPS: already right-orthogonalized
            timeEvo (tdevott.timeEvolution): class for time evolution
            file (file object): file for results
    """

    totalStep = len(TTs.omegaQSeq[0])
    dataSize = int(totalStep / stride)
    mod = int(totalStep % stride)

    for i in range(dataSize):
        for j in range(stride):
            stepNum = i * stride + j
            time = dtFB * stepNum
            timeEvo.zTTTimeEvo(TTs.rho, TTs.H, time, stepNum)
        
        stepNum = (i+1) * stride
        outTime = f'{dtFB * (i+1) * stride: .15e},'
        rhoOut = getRotatingRDO(dtFB, stepNum, TTs).flatten()
        outRho = ','.join(f'{elem.real: .15e},{elem.imag: .15e}'
                          for elem in rhoOut)
        outStr = outTime + outRho + '\n'

        file.write(outStr)

    if mod > 0:
        for i in range(mod):
            stepNum = dataSize*stride + i
            time = dtFB * stepNum
            timeEvo.zTTTimeEvo(TTs.rho, TTs.H, time, stepNum)

        stepNum = totalStep
        outTime = f'{dtFB * totalStep: .15e},'
        rhoOut = getRotatingRDO(dtFB, stepNum, TTs).flatten()
        outRho = ','.join(f'{elem.real: .15e},{elem.imag: .15e}'
                          for elem in rhoOut)
        outStr = outTime + outRho + '\n'

        file.write(outStr)
    
    # apply virtual Z gates
    stepNum = totalStep
    outTime = f'{dtFB * totalStep: .15e},'
    rhoOut = getRotatingRDO(dtFB, stepNum, TTs)
    rhoOut = TTs.matVZ @ rhoOut @ TTs.matVZ.conj().T
    rhoOut = rhoOut.flatten()
    outRho = ','.join(f'{elem.real: .15e},{elem.imag: .15e}'
                        for elem in rhoOut)
    outStr = outTime + outRho + '\n'

    file.write(outStr)

def outputCurrentStates(dt: float, stepNum: int, TTs: TTs, file):
    """output current reduced density operator
        Mainly used for writing initial states

        params:
            dt (float): time step of TTs.omegaQSeq
            stepNum (int): current step number
            TTs (TTs.TTs): MPS and MPO
            file (file object): file for results
    """

    time = stepNum * dt
    rhoOut = getRotatingRDO(dt, stepNum, TTs).flatten()
    outTime = f'{time: .15e},'
    outRho = ','.join(f'{elem.real: .15e},{elem.imag: .15e}'
                          for elem in rhoOut)
    outStr = outTime + outRho + '\n'

    file.write(outStr)

def getRotatingRDO(dt: float, stepNum: int, TTs: TTs):
    """transform the reduced density operator in the lab frame
        to that in the rorating frame

        params:
            dt (float): time step of TTs.omegaQSeq
            stepNum (int): current step number
            TTs (TTs): MPS and MPO
        
        returns:
            numpy.ndarray: RDO in the rorating frame
    """

    rdo = TTs.getRDO()

    angleList = []
    seqTmp = np.zeros(len(TTs.omegaQSeq[0])+1)

    for i in range(TTs.numQ):
        seqTmp[:-1] = TTs.omegaQSeq[i][:]
        seqTmp[-1] = TTs.omegaQSeq[i][-1]
        angleList.append(simpson(seqTmp[:stepNum+1], dx=dt))

    rot = np.array([1], dtype=np.complex128)
    for i in range(TTs.numQ-1, -1, -1):
        rot = np.kron(RZ(angleList[i]), rot)

    rdo = rot @ rdo @ rot.conj().T

    return rdo

def RZ(theta: float):
    """RZ rotation with the angle theta

        params:
            theta (float): angle

        returns:
            numpy.ndarray: roration matrix
    """

    return np.array([[np.exp(-0.5j*theta), 0],
                     [0, np.exp(0.5j*theta)]])