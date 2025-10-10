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
        
        rhoOut = TTs.getRDO()
        outTime = f'{dtFB * (i+1) * stride: .15e},'
        outRho = ','.join(f'{elem.real: .15e},{elem.imag: .15e}'
                          for elem in rhoOut)
        outStr = outTime + outRho + '\n'

        file.write(outStr)

    if mod > 0:
        for i in range(mod):
            stepNum = dataSize*stride + i
            time = dtFB * stepNum
            timeEvo.zTTTimeEvo(TTs.rho, TTs.H, time, stepNum)

        rhoOut = TTs.getRDO()
        outTime = f'{dtFB * totalStep: .15e},'
        outRho = ','.join(f'{elem.real: .15e},{elem.imag: .15e}'
                          for elem in rhoOut)
        outStr = outTime + outRho + '\n'

        file.write(outStr)        

def outputCurrentStates(currentTime: float, TTs: TTs, file):
    """output current reduced density operator
        Mainly used for writing initial states

        params:
            currentTime (float): currentTime
            TTs (TTs.TTs): MPS and MPO
            file (file object): file for results
    """

    rhoOut = TTs.getRDO()
    outTime = f'{currentTime: .15e},'
    outRho = ','.join(f'{elem.real: .15e},{elem.imag: .15e}'
                          for elem in rhoOut)
    outStr = outTime + outRho + '\n'

    file.write(outStr)