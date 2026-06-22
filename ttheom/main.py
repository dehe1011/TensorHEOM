import os
import scipy.constants as c
import numpy as np

from .bath import getBathParams
from .pulse import setGates
from .tt import TTs1Q, TTs2QId, TTsMQChainId
from .circuit import setPulseSeq
from .dynamics import timeEvolution, outputCurrentStates, calcDynamics
from .ssh import saveQC, loadQC

def prepareBathArgs(rho, omegaQmax, T, T1, omegaC, exp, tol):

    if not isinstance(T, list) and not isinstance(T, np.ndarray):
        T = [T] * rho['numQ']
    if not isinstance(T1, list) and not isinstance(T1, np.ndarray):
        T1 = [T1] * rho['numQ']
    if not isinstance(omegaC, list) and not isinstance(omegaC, np.ndarray):
        omegaC = [omegaC] * rho['numQ']
    if not isinstance(exp, list) and not isinstance(exp, np.ndarray):
        exp = [exp] * rho['numQ']
    if not isinstance(tol, list) and not isinstance(tol, np.ndarray):
        tol = [tol] * rho['numQ']
    
    beta = c.hbar * omegaQmax * 1e9 / (np.array(T) * 1e-3 * c.k)
    kappa = 1 / (omegaQmax * 1e9 * np.array(T1) * 1e-6 * 2 * np.pi)
    bath = [{'type': 'broadband', 'beta': float(beta[i]), 'kappa': float(kappa[i]), 
            'omegaC': omegaC[i], 'exp': exp[i], 'tol': tol[i]} for i in range(rho['numQ'])]
    
    return bath

def prepareGateArgs(rho, omegaQmax, gateTime):
    gateList = []
    for i in range(rho['numQ']):
        kwargs1Q = {'omega': float(-rho['omegaQ'][i]), 'gateTime': float(omegaQmax * gateTime[i]) }
        gateList.append([[i], 'rxyStep', kwargs1Q])
    for i in range(rho['numQ']-1):
        kwargs2Q = {'gateTime': float(omegaQmax * gateTime[rho['numQ'] + i]) }
        gateList.append([[i, i+1], 'directCplStepVarJ', kwargs2Q])
    return gateList

def prepareSystemArgs(numQ, freqQ, rhoIni=None, idlingTime=None, gateTime=None):
    omegaQ = 2*np.pi*np.array(freqQ)
    omegaQmax = max(omegaQ)
    omegaQ /= omegaQmax
    if rhoIni is None:
        rhoIni = np.zeros((2**numQ, 2**numQ), dtype=np.complex128)
        rhoIni[0, 0] = 1
    else:
        rhoIni = np.array(rhoIni, dtype=np.complex128)
    rho = {'numQ': numQ, 'rhoIni': rhoIni, 'omegaQ': omegaQ.tolist()}
    return omegaQmax, rho

def prepareArgs(numQ, freqQ, gateTime, T, T1, omegaC, exp, tol, rhoIni, idlingTime, dtFB, depth, bondDim):
    omegaQmax, rho = prepareSystemArgs(numQ, freqQ, rhoIni=rhoIni, idlingTime=idlingTime, gateTime=gateTime)
    gateList = prepareGateArgs(rho, omegaQmax, gateTime)
    bath = prepareBathArgs(rho, omegaQmax, T, T1, omegaC, exp, tol)

    dtFB *= omegaQmax * 1e-3
    idlingTime *= omegaQmax
    V = np.array([[[0, 1],[1, 0]] for _ in range(rho['numQ'])], dtype=np.complex128)
    args = omegaQmax, rho, bondDim, V, depth, bath, gateList, dtFB, idlingTime
    return args

def reverseBathArgs(omegaQmax, bath):
    T = c.hbar * omegaQmax * 1e9 / (np.array([b['beta'] for b in bath]) * 1e-3 * c.k)
    T1 = 1 / (omegaQmax * 1e9 * np.array([b['kappa'] for b in bath]) * 1e-6 * 2 * np.pi)
    omegaC = [b['omegaC'] for b in bath]
    exp = [b['exp'] for b in bath]
    tol = [b['tol'] for b in bath]
    return T, T1, omegaC, exp, tol

def reverseGateArgs(rho, omegaQmax, gateList):
    gateTime = [gateList[i][2]['gateTime']/omegaQmax for i in range(2*rho['numQ']-1) ]
    return gateTime

def reverseSystemArgs(omegaQmax, rho):
    numQ = rho['numQ']
    freQ = np.array(rho['omegaQ']) * omegaQmax / (2*np.pi)
    rhoIni = np.array(rho['rhoReal']) + 1j * np.array(rho['rhoImag'])
    return numQ, freQ.tolist(), rhoIni

def reverseArgs(omegaQmax, rho, bondDim, V, depth, bath, gateList, dtFB, idlingTime):
    numQ, freqQ, rhoIni = reverseSystemArgs(omegaQmax, rho)
    T, T1, omegaC, exp, tol = reverseBathArgs(omegaQmax, bath)
    gateTime = reverseGateArgs(rho, omegaQmax, gateList)
    return numQ, freqQ, gateTime, T, T1, omegaC, exp, tol, rhoIni, idlingTime/omegaQmax, dtFB/(omegaQmax*1e-3), depth, bondDim

def getArgs(directory, fileName):
    qcFilePath = os.path.join(os.getcwd(), directory, 'qcData_' + fileName + '.qpy')
    qc = loadQC(qcFilePath)
    metadata = qc.metadata
    omegaQmax, rho, bondDim, V, depth, bath, gateList, dtFB, idlingTime = metadata['omegaQmax'], metadata['rho'], metadata['bondDim'], None, metadata['depth'], metadata['bath'], metadata['gateList'], metadata['dtFB'], metadata['idlingTime']
    numQ, freqQ, gateTime, T, T1, omegaC, exp, tol, rhoIni, idlingTime, dtFB, depth, bondDim = reverseArgs(omegaQmax, rho, bondDim, V, depth, bath, gateList, dtFB, idlingTime)
    kwargs = {
        "directory": directory,
        "fileName": fileName,
        "numQ": numQ,
        "freqQ": freqQ, # GHz
        "gateTime": gateTime, # ns
        "T": T, # mK
        "T1": T1, # us
        "omegaC": omegaC,
        "exp": exp,
        "tol": tol,
        "idlingTime": idlingTime, # ns
        "dtFB": dtFB, # fs
        "depth": depth,
        "bondDim": bondDim,
        "strideTime": metadata['stride'] * metadata['dtFB']/ metadata['omegaQmax'], # ns
        "useRFPlus": metadata['useRFPlus'],
        "isRK13": metadata['isRK13'],
    }

    rho = metadata['rho']
    rhoIni = np.array(rho['rhoReal']) + 1j * np.array(rho['rhoImag'])
    rhoIni.reshape(2**rho['numQ'], 2**rho['numQ'])
    kwargs["rhoIni"] = rhoIni
    kwargs["qc"] = qc
    return kwargs

def prepareTTs(fileName, qc, numQ, freqQ, gateTime, T, T1, omegaC, exp, tol, rhoIni, idlingTime, dtFB, depth, bondDim, strideTime, useRFPlus=False, isRK13=False, directory=None):
    """main function for simulation
        Dynamics of the reduced density operator are written in fileName.
    
        args:
            qc (qiskit.QuantumCircuit): quantum circuit for simulation
            idlingTime (float): idling time, in the unit of omegaQmax
            gateList (list): list for qubit gates
            rho (dict): properties of systems
                rho['numQ']: number of qubits
                rho['rhoIni'] (numpy.ndarray): initial reduced density matrix
                rho['omegaQ'] (list): list of qubit frequency
            bath (list): list of bath parameters
                each element of the list is a dict of bath parameter values
            dtFB (float): step width for forward + backward time integration
            depth (list[int]): list of hierarchy depth for each bath
            bondDim (int): bond dimension for MPS and MPO
            useRFPlus (bool): whether Redfield+ method is used (True)
                or not (False)
    """
    print(directory)

    if useRFPlus:
        depth  = [1] * len(depth)   

    stride = int(strideTime / (dtFB*1e-3))
    omegaQmax, rho, bondDim, V, depth, bath, gateList, dtFB, idlingTime = prepareArgs(numQ, freqQ, gateTime, T, T1, omegaC, exp, tol, rhoIni, idlingTime, dtFB, depth, bondDim)
    
    # set filepath and save qc data
    if directory is not None:
        os.makedirs(directory, exist_ok=True)
        qcFilePath = os.path.join(os.getcwd(), directory, 'qcData_' + fileName)
    else:
        qcFilePath = 'qcData_' + fileName
    params = saveQC(qcFilePath, omegaQmax, qc, idlingTime, gateList, rho, bath, V, dtFB, stride, depth, bondDim, isRK13=isRK13, useRFPlus=useRFPlus)
    print(f"Saved quantum circuit data to {qcFilePath}.")
    print(params)

    # Connecting quantum gates and pulse sequence
    pulse, pulseMap = setGates(gateList)
    
    # Decomposition of bath correlation functions
    nu = []
    coeff = []
    for i in range(rho['numQ']):
        nuTmp, coeffTmp = getBathParams(bath[i])
        
        nu.append(nuTmp)
        coeff.append(coeffTmp)

    # Initialize Tensor Train structure
    if rho['numQ'] == 1:
        TTs = TTs1Q(rho['rhoIni'], bondDim, V, depth, nu, coeff,
                    pulse, pulseMap)
    elif rho['numQ'] == 2:
        TTs = TTs2QId(rho['rhoIni'], bondDim, V, depth, nu, coeff,
                      pulse, pulseMap)
    elif rho['numQ'] >= 3:
        TTs = TTsMQChainId(rho['numQ'], rho['rhoIni'], bondDim, V, depth,
                           nu, coeff, pulse, pulseMap)
    else:
        raise ValueError(
            f"Invalid number of qubits: expected an integer ≥ 1, got {rho['numQ']}."
        )

    # Compilation qiskit qc into pulse sequence
    _ = setPulseSeq(qc, TTs, rho['omegaQ'], dtFB, idlingTime)

    return TTs, params

def calcTimeEvo(fileName, qc, numQ, freqQ, gateTime, T, T1, omegaC, exp, tol, rhoIni, idlingTime, dtFB, depth, bondDim, strideTime, useRFPlus=False, isRK13=False, directory=None):

    # setup tensor trains
    TTs, params = prepareTTs(fileName, qc, numQ, freqQ, gateTime, T, T1, omegaC, exp, tol, rhoIni, idlingTime, dtFB, depth, bondDim, strideTime, useRFPlus=useRFPlus, isRK13=isRK13, directory=directory)

    dtFB = params['dtFB']
    stride = params['stride']
    isRK13 = params['isRK13']

    # set filepath and save qc data
    if directory is not None:
        os.makedirs(directory, exist_ok=True)
        csvFilePath = os.path.join(os.getcwd(), directory, fileName+'.csv')
    else:
        csvFilePath = fileName+'.csv'
    print(f"Saved result data to {csvFilePath}.")

    # Time evolution
    timeEvo = timeEvolution(TTs, 0.5*dtFB, isRK13)

    with open(csvFilePath, 'w', encoding='utf-8') as file:
        stepNum = 0
        outputCurrentStates(dtFB, stepNum, TTs, file)
        calcDynamics(dtFB, stride, TTs, timeEvo, file)

def main(fileName, qc, idlingTime, gateList, rho,
         bath, V, dtFB, stride, depth, bondDim, isRK13=False,
         useRFPlus=False):
    """main function for simulation
        Dynamics of the reduced density operator are written in fileName.
    
        args:
            fileName (str): file name for output
            qc (qiskit.QuantumCircuit): quantum circuit for simulation
            idlingTime (float): idling time, in the unit of omegaQ[0] 
            gateList (list): list for qubit gates
            rho (dict): properties of systems
                rho['numQ']: number of qubits
                rho['rhoIni'] (numpy.ndarray): initial reduced density matrix
                rho['omegaQ'] (list): list of qubit frequency                
            bath (list): list of bath parameters
                each element of the list is a dict of bath parameter values
            V (numpy.ndarray): 3d array of system-bath coupling
                V[j, :, :]: system operator coupled with j th bath
            dtFB (float): step width for forward + backward time integration
            stride (int): loops per output
            isRK13 (bool): Runge-Kutta method
                True: 13-stage 5th-order Runge-Kutta
                False: 5-stage 4th-order Runge-Kutta
            useRFPlus (bool): whether Redfield+ method is used (True)
                or not (False)
    """

    if useRFPlus:
        depth  = [1] * len(depth)

    # Decomposition of bath correlation functions
    nu = []
    coeff = []
    for i in range(rho['numQ']):
        nuTmp, coeffTmp = getBathParams(bath[i])
        
        nu.append(nuTmp)
        coeff.append(coeffTmp)
    
    # Connecting quantum gates and pulse sequence
    pulse, pulseMap = setGates(gateList)

    # Initialize Tensor Train structure
    if rho['numQ'] == 1:
        TTs = TTs1Q(rho['rhoIni'], bondDim, V, depth, nu, coeff,
                    pulse, pulseMap)
    elif rho['numQ'] == 2:
        TTs = TTs2QId(rho['rhoIni'], bondDim, V, depth, nu, coeff,
                      pulse, pulseMap)
    elif rho['numQ'] >= 3:
        TTs = TTsMQChainId(rho['numQ'], rho['rhoIni'], bondDim, V, depth,
                           nu, coeff, pulse, pulseMap)
    else:
        raise ValueError(
            f"Invalid number of qubits: expected an integer ≥ 1, got {rho['numQ']}."
        )

    # Compilation qiskit qc into pulse sequence
    setPulseSeq(qc, TTs, rho['omegaQ'], dtFB, idlingTime)

    # Time evolution
    timeEvo = timeEvolution(TTs, 0.5*dtFB, isRK13)

    with open(fileName, 'w', encoding='utf-8') as file:
        stepNum = 0
        outputCurrentStates(dtFB, stepNum, TTs, file)
        calcDynamics(dtFB, stride, TTs, timeEvo, file)