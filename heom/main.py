import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

from .tt.TTs1Q import TTs1Q
from .tt.TTs2QId import TTs2QId
from .tdevott import timeEvolution
from .dynamics import outputCurrentStates, calcDynamics
from .bath.params import getBathParams
from .pulse.set_gates import setGates
from .circuit.pulse_seq import setPulseSeq

def main(fileName, qc, idlingTime, gateList, rho,
         bath, V, dtFB, stride, depth, bondDim, isRK13=False,
         useRFPlus=False):
    """main function for simulation
        Dyanmics of the reduced density operator are written in fileName.
    
        params:
            fileName (str): file name for output
            qc (qiskit.QuantumCircuit): quantum circuit for simulation
            idlingTime (float): idling time, in the unit of omegaQ[0] 
            gateList (list): list for qubit gates
            rho (dict): properties of systems
                rho['numQ']: number of qubits
                rho['rhoIni'] (numpy.ndarray): initial reduced density matrix
                rho['omegaQ'] (list): list of qubit frequency                
            bath (list): list of bath name
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

    nu = []
    coeff = []
    for i in range(rho['numQ']):
        nuTmp, coeffTmp = getBathParams(bath[i])
        
        nu.append(nuTmp)
        coeff.append(coeffTmp)
    
    pulse, pulseMap = setGates(gateList)

    if useRFPlus:
        depth  = [1] * len(depth)

    if rho['numQ'] == 1:
        TTs = TTs1Q(rho['rhoIni'], bondDim, V, depth, nu, coeff,
                    pulse, pulseMap)
    elif rho['numQ'] == 2:
        TTs = TTs2QId(rho['rhoIni'], bondDim, V, depth, nu, coeff,
                      pulse, pulseMap)
    
    setPulseSeq(qc, TTs, rho['omegaQ'], dtFB, idlingTime)
    timeEvo = timeEvolution(TTs, 0.5*dtFB, isRK13)

    with open(fileName, 'w') as file:
        currentTime = 0.0
        outputCurrentStates(currentTime, TTs, file)

        calcDynamics(dtFB, stride, TTs, timeEvo, file)