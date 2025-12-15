import getpass
from qiskit import QuantumCircuit
import numpy as np
from heom.ssh.job_control import submitJob

def run3():
    qc = QuantumCircuit(3)
    qc.h(0)

    idlingTime = 0

    rho = {'numQ': 3}
    rhoIni = np.zeros([8, 8], dtype=np.complex128)
    rhoIni[0, 0] = 1
    rho['rhoIni'] = rhoIni
    
    rho['omegaQ'] = [1., 1., 1.] # in the order: [qubit 2, qubit 1, qubit 0]

    gateTime1Q = 1 # 160 * np.pi # 16ns
    kwargs1Q = [{'omega': -rho['omegaQ'][2], 'gateTime': gateTime1Q},
                {'omega': -rho['omegaQ'][1], 'gateTime': gateTime1Q},
                {'omega': -rho['omegaQ'][0], 'gateTime': gateTime1Q},]
    
    kwargs2Q = {'gateTime': 500 * np.pi} # 50ns

    gateList = [[[0], 'rxyStep', kwargs1Q[0]],
                [[1], 'rxyStep', kwargs1Q[1]],
                [[2], 'rxyStep', kwargs1Q[2]],
                [[0, 1], 'directCplStepVarJ', kwargs2Q],
                [[1, 2], 'directCplStepVarJ', kwargs2Q],]
    
    bathParams = {'type': 'broadband'}
    bathParams['beta'] = 8 # 30 mK
    bathParams['kappa'] = 1e-6 / 2 / np.pi # T1: 32 us
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

    dtFB = 0.002 # 0.001

    strideTime = 1

    stride = int(strideTime // dtFB)

    depth = [1, 1, 1]
    bondDim = 5

    submissionParams = {}
    submissionParams['hostname'] = 'justus2.uni-ulm.de'
    submissionParams['schedulerName'] = 'slurm'
    submissionParams['numNodes'] = 1
    submissionParams['cpusPerTask'] = 4
    submissionParams['maxTime'] = '336:00:00'
    submissionParams['others'] = ''
    submissionParams['venvPath'] = '$HOME/python_HEOM/.venv'

    submissionParams['username'] = input('User Name: ')
    submissionParams['emailAddress'] = input('Email Address: ')
    submissionParams['otp'] = getpass.getpass('Your OTP: ')
    submissionParams['password'] = getpass.getpass('Password: ')
    submitJob(submissionParams, qc, idlingTime, gateList, rho,
              bath, V, dtFB, stride, depth, bondDim, useRFPlus=True)

if __name__ == '__main__':
    run3()