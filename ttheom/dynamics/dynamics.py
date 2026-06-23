from time import time
from tqdm import tqdm
import numpy as np
from scipy.integrate import simpson
from ..tt.TTs import TTs
from .tdevott import timeEvolution

def calcDynamics(dtFB: float, stride: int,
                 TTs: TTs, timeEvo: timeEvolution, file):
    """Run the time evolution and write the reduced density operator to a file.

    Parameters
    ----------
    dtFB : float
        Step width for forward + backward time integration.
    stride : int
        Number of integration steps between successive outputs.
    TTs : TTs.TTs
        MPS and MPO; the MPS must already be right-orthogonalized.
    timeEvo : tdevott.timeEvolution
        Time evolution object.
    file : file object
        Open file for writing results.
    """

    totalStep = len(TTs.omegaQSeq[0])
    print(f'Total step: {totalStep}')
    dataSize = int(totalStep / stride)
    mod = int(totalStep % stride)

    for i in tqdm(range(dataSize)):
        for j in range(stride):
            stepNum = i * stride + j
            t = dtFB * stepNum
            timeEvo.zTTTimeEvo(TTs.rho, TTs.H, t, stepNum)

        stepNum = (i+1) * stride
        outTime = f'{dtFB * (i+1) * stride: .15e},'
        rhoOut = getRotatingRDO(dtFB, stepNum, TTs)
        rhoOut = TTs.permMat @ rhoOut @ TTs.permMat.T
        rhoOut = rhoOut.flatten()
        outRho = ','.join(f'{elem.real: .15e},{elem.imag: .15e}'
                          for elem in rhoOut)
        outStr = outTime + outRho + '\n'

        file.write(outStr)

    if mod > 0:
        for i in range(mod):
            stepNum = dataSize*stride + i
            t = dtFB * stepNum
            timeEvo.zTTTimeEvo(TTs.rho, TTs.H, t, stepNum)

        stepNum = totalStep
        outTime = f'{dtFB * totalStep: .15e},'
        rhoOut = getRotatingRDO(dtFB, stepNum, TTs)
        rhoOut = TTs.permMat @ rhoOut @ TTs.permMat.T
        rhoOut = rhoOut.flatten()
        outRho = ','.join(f'{elem.real: .15e},{elem.imag: .15e}'
                          for elem in rhoOut)
        outStr = outTime + outRho + '\n'

        file.write(outStr)

    # apply virtual Z gates
    stepNum = totalStep
    outTime = f'{dtFB * totalStep: .15e},'
    rhoOut = getRotatingRDO(dtFB, stepNum, TTs)
    rhoOut = TTs.matVZ @ rhoOut @ TTs.matVZ.conj().T
    rhoOut = TTs.permMat @ rhoOut @ TTs.permMat.T
    rhoOut = rhoOut.flatten()
    outRho = ','.join(f'{elem.real: .15e},{elem.imag: .15e}'
                        for elem in rhoOut)
    outStr = outTime + outRho + '\n'

    file.write(outStr)

def outputCurrentStates(dt: float, stepNum: int, TTs: TTs, file):
    """Write the current reduced density operator to a file.

    Mainly used for recording the initial state.

    Parameters
    ----------
    dt : float
        Time step of ``TTs.omegaQSeq``.
    stepNum : int
        Current step number.
    TTs : TTs.TTs
        MPS and MPO.
    file : file object
        Open file for writing results.
    """

    t = stepNum * dt
    rhoOut = getRotatingRDO(dt, stepNum, TTs)
    rhoOut = TTs.permMat @ rhoOut @ TTs.permMat.T
    rhoOut = rhoOut.flatten()
    outTime = f'{t: .15e},'
    outRho = ','.join(f'{elem.real: .15e},{elem.imag: .15e}'
                          for elem in rhoOut)
    outStr = outTime + outRho + '\n'

    file.write(outStr)

def getRotatingRDO(dt: float, stepNum: int, TTs: TTs):
    """Transform the reduced density operator from the lab frame to the rotating frame.

    Parameters
    ----------
    dt : float
        Time step of ``TTs.omegaQSeq``.
    stepNum : int
        Current step number.
    TTs : TTs.TTs
        MPS and MPO.

    Returns
    -------
    numpy.ndarray
        Reduced density operator in the rotating frame.
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
    """Compute the single-qubit Z-rotation matrix.

    Parameters
    ----------
    theta : float
        Rotation angle in radians.

    Returns
    -------
    numpy.ndarray
        :math:`2 \\times 2` rotation matrix
        :math:`\\operatorname{diag}(e^{-i\\theta/2},\\, e^{i\\theta/2})`.
    """

    return np.array([[np.exp(-0.5j*theta), 0],
                     [0, np.exp(0.5j*theta)]])
