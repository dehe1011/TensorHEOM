from qiskit import QuantumCircuit
import numpy as np
from .. import main

def run1():
    fileName = 'rdo_1qubit.csv'

    qc = QuantumCircuit(1)
    qc.rx(0.5*np.pi, 0)
    qc.delay(0, 0)
    qc.ry(0.5*np.pi, 0)
    qc.delay(0, 0)
    qc.ry(-0.5*np.pi, 0)

    idlingTime = 0.1

    rho = {'numQ': 1}
    rho['rhoIni'] = np.array([[1, 0],
                              [0, 0]], dtype=np.complex128)
    rho['omegaQ'] = [1.]

    gateList = [[[0], 'rxyStep', ]]
    kwargs1Q = {'omega': -rho['omegaQ'][0], 'gateTime': 0.1 * np.pi}
    gateList = [[[0], 'rxyStep', kwargs1Q]]

    bath = ['s=1']

    V = np.array([
        [[0, 1],
         [1, 0]]
    ], dtype=np.complex128)

    dtFB = 0.001

    strideTime = 0.01

    stride = int(strideTime / dtFB)

    main(fileName, qc, idlingTime, gateList, rho,
         bath, V, dtFB, stride)
    
if __name__ == '__main__':
    run1()