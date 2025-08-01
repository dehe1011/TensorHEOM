from .TTs import TTs
from .tdevott import timeEvolution
from .opett import zOutMPS

def calcDynamics(params: dict, dtFB: float, stride: int,
                 TTs: TTs, timeEvo: timeEvolution):
    """conduct calculation according to params
    
        params:
            params (dict): dictionary gate parameters
                params['time'] (float): simulation time
                params['omega'] (numpy.ndarray): 1d array of drive frequency
                params['amp'] (numpy.ndarray): 1d array of drive amplitude
                params['phase'] (numpy.ndarray): 1d array of initial phase
                params['omegaQ'] (list): list of qubit frequency
                params['J'] (list): list of coupling strength between two qubits
                params['currentTime'] (float): current time in simulation
            dtFB (float): step width for forward + backward time integration
            stride (int): loops per output
            TTs (TTs.TTs): MPS and MPO
                MPS: already right-orthogonalized
            timeEvo (tdevott.timeEvolution): class for time evolution

        returns:
            outData (list): 2d list of output
    """

    totalStep = int(params['time'] / dtFB)
    dataSize = int(totalStep / stride)
    mod = int(totalStep % stride)

    timeEvo.setFieldParams(params['omega'], params['amp'], params['phase'])
    TTs.changeFreq(params['omegaQ'])
    TTs.changeCpl(params['J'])

    outData = []
    for i in range(dataSize):
        for j in range(stride):
            time = params['currentTime'] + dtFB * (i * stride + j)
            timeEvo.zTTTimeEvo(TTs.rho, TTs.H, time)

        outTmp = [params['currentTime'] + dtFB * (i+1) * stride]
        for idx in TTs.indices:
            outTmp.append(zOutMPS(TTs.rho, idx))
        outData.append(outTmp)
    
    if mod > 0:
        for i in range(mod):
            time = params['currentTime'] \
                + dtFB * (dataSize*stride + i)
            timeEvo.zTTTimeEvo(TTs.rho, TTs.H, time)

        outTmp = [params['currentTime'] + dtFB * totalStep]
        for idx in TTs.indices:
            outTmp.append(zOutMPS(TTs.rho, idx))
        outData.append(outTmp)

    return outData

def outputCurrentStates(currentTime: float, TTs: TTs):
    """output current reduced density operator

        params:
            currentTime (float): currentTime
            TTs (TTs.TTs): MPS and MPO

        returns:
            outData (list): output
    """

    outData = [[currentTime]]

    for idx in TTs.indices:
        outData[0].append(zOutMPS(TTs.rho, idx))

    return outData