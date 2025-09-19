from qiskit import QuantumCircuit
import numpy as np
from .. import main

def run():
    fileName = 'rdo_2qubit01.csv'

    qc = QuantumCircuit(2)
    qc.ry(-0.5*np.pi, 1)
    qc.rx(0.5*np.pi, 0)
    qc.iswap(0, 1)
    qc.ry(-0.5*np.pi, 1)
    qc.iswap(0, 1)

    idlingTime = 0.0

    rho = {'numQ': 2}
    rho['rhoIni'] = np.array([[1, 0, 0, 0],
                              [0, 0, 0, 0],
                              [0, 0, 0, 0],
                              [0, 0, 0, 0]], dtype=np.complex128)
    
    rho['omegaQ'] = [1., 1.] # in the order: [qubit 1, qubit 0]

    kwargs1Q = [{'omega': -rho['omegaQ'][0], 'gateTime': 0.1},
                {'omega': -rho['omegaQ'][1], 'gateTime': 0.1},]
    
    kwargs2Q = {'gateTime': 0.05}

    gateList = [[[0], 'rxyStep', kwargs1Q[0]],
                [[1], 'rxyStep', kwargs1Q[1]],
                [[0, 1], 'directCplStepVarJ', kwargs2Q]]
    
    bath = ['s=1', 's=1'] # in the order: [qubit 1, qubit 0]

    V = np.array([
        [[0, 1],
         [1, 0]],

        [[0, 1],
         [1, 0]]
    ], dtype=np.complex128) # in the order: [qubit 1, qubit 0]

    dtFB = 0.001

    strideTime = 0.01

    stride = int(strideTime // dtFB)

    main(fileName, qc, idlingTime, gateList, rho,
         bath, V, dtFB, stride)
    
if __name__ == '__main__':
    run()