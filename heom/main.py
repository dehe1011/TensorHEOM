from .bath import getBathParams
from .pulse import setGates
from .tt import TTs1Q, TTs2QId, TTsMQChainId
from .circuit import setPulseSeq
from .dynamics import timeEvolution, outputCurrentStates, calcDynamics

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