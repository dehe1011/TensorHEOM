from qiskit import QuantumCircuit
import numpy as np
from ttheom.main import main

def run_1q_realistic():
    fileName = 'rdo_1qubit_realistic.csv'

    qc = QuantumCircuit(1)
    qc.rx(0.5*np.pi, 0)
    qc.delay(0, 0)
    qc.ry(0.5*np.pi, 0)
    qc.delay(0, 0)
    qc.ry(-0.5*np.pi, 0)

    idlingTime = 10*np.pi # 1 ns

    rho = {'numQ': 1}
    rho['rhoIni'] = np.array([[1, 0],
                              [0, 0]], dtype=np.complex128)
    rho['omegaQ'] = [1.]

    gateList = [[[0], 'rxyStep', ]]
    # gate time: 16 ns
    kwargs1Q = {'omega': -rho['omegaQ'][0], 'gateTime': 160 * np.pi}
    gateList = [[[0], 'rxyStep', kwargs1Q]]

    bath = [{'type': 'broadband'}]
    bath[0]['beta'] = 8 # 30 mK
    bath[0]['kappa'] = 1e-6 / 2 / np.pi # T1: 32 us
    bath[0]['omegaC'] = 50
    bath[0]['exp'] = 1
    bath[0]['tol'] = 1e-6

    V = np.array([
        [[0, 1],
         [1, 0]]
    ], dtype=np.complex128)

    dtFB = 0.005 # 0.001

    strideTime = 3

    stride = int(strideTime / dtFB)

    depth = [1]
    bondDim = 5

    main(fileName, qc, idlingTime, gateList, rho,
         bath, V, dtFB, stride, depth, bondDim, useRFPlus=True)
    
if __name__ == '__main__':
    run_1q_realistic()