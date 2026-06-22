from qiskit import QuantumCircuit
import numpy as np
from ttheom.main import main

def run_3q():
    fileName = 'rdo_3qubit.csv'

    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.ccx(0, 1, 2)

    idlingTime = 0 # 0.005

    rho = {'numQ': 3}
    rhoIni = np.zeros([8, 8], dtype=np.complex128)
    rhoIni[0, 0] = 1
    rho['rhoIni'] = rhoIni
    
    rho['omegaQ'] = [1., 1., 1.] # in the order: [qubit 2, qubit 1, qubit 0]

    kwargs1Q = [{'omega': -rho['omegaQ'][2], 'gateTime': 0.1},
                {'omega': -rho['omegaQ'][1], 'gateTime': 0.1},
                {'omega': -rho['omegaQ'][0], 'gateTime': 0.1},]
    
    kwargs2Q = {'gateTime': 0.05}

    gateList = [[[0], 'rxyStep', kwargs1Q[0]],
                [[1], 'rxyStep', kwargs1Q[1]],
                [[2], 'rxyStep', kwargs1Q[2]],
                [[0, 1], 'directCplStepVarJ', kwargs2Q],
                [[1, 2], 'directCplStepVarJ', kwargs2Q],]
    
    bathParams = {'type': 'broadband'}
    bathParams['beta'] = 5
    bathParams['kappa'] = 0.004 / 2 / np.pi
    bathParams['omegaC'] = 50
    bathParams['exp'] = 1
    bathParams['tol'] = 1e-6
    
    bath = [bathParams, bathParams, bathParams] 
    # in the order: [qubit 2, qubit 1, qubit 0]

    V = np.array([
        [[0, 1],
         [1, 0]],

        [[0, 1],
         [1, 0]],

        [[0, 1],
         [1, 0]]
    ], dtype=np.complex128) # in the order: [qubit 2, qubit 1, qubit 0]

    dtFB = 0.001

    strideTime = 0.01

    stride = int(strideTime // dtFB)

    depth = [2, 2, 2]
    bondDim = 20
    main(fileName, qc, idlingTime, gateList, rho,
         bath, V, dtFB, stride, depth, bondDim)
    
if __name__ == '__main__':
    run_3q()