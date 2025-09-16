from .TTs import TTs
from .tdevott import timeEvolution
from .opett import zOutMPS

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
        
        outStr = f'{dtFB * (i+1) * stride: .15e}'
        for idx in TTs.indices:
            rhoElement = zOutMPS(TTs.rho, idx)
            outStr += f',{rhoElement.real: .15e},{rhoElement.imag: .15e}'        
        outStr += '\n'

        file.write(outStr)

    if mod > 0:
        for i in range(mod):
            stepNum = dataSize*stride + i
            time = dtFB * stepNum
            timeEvo.zTTTimeEvo(TTs.rho, TTs.H, time, stepNum)

        outStr = f'{dtFB * totalStep: .15e}'
        for idx in TTs.indices:
            rhoElement = zOutMPS(TTs.rho, idx)
            outStr += f',{rhoElement.real: .15e},{rhoElement.imag: .15e}'        
        outStr += '\n'

        file.write(outStr)        

def outputCurrentStates(currentTime: float, TTs: TTs, file):
    """output current reduced density operator
        Mainly used for writing initial states

        params:
            currentTime (float): currentTime
            TTs (TTs.TTs): MPS and MPO
            file (file object): file for results
    """

    outStr = f'{currentTime: .15e}'

    for idx in TTs.indices:
        rhoElement = zOutMPS(TTs.rho, idx)
        outStr += f',{rhoElement.real: .15e},{rhoElement.imag: .15e}'
    outStr += '\n'

    file.write(outStr)