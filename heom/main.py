import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

from .TTs1Q import TTs1Q
from .TTs2QId import TTs2QId
from .tdevott import timeEvolution
from .dynamics import outputCurrentStates, calcDynamics
from .bath import getBathParams
from .circuit.pulse_seq import setPulseSeq

def main(fileName, qc, idlingTime, pulse, map, rho,
         bath, V, dtFB, stride, isRK13=False):
    """main function for simulation
        Dyanmics of the reduced density operator are written in fileName.
    
        params:
            fileName (str): file name for output
            qc (qiskit.QuantumCircuit): quantum circuit for simulation
            idlingTime (float): idling time, in the unit of omegaQ[0] 
            pulse (list[
                list[list[qubitIdx], pulse.abstract_pulse.abstractPulse]
                ]):
            map (dict[tuple[int]: int]): dictionary for a mapping from
                qubit indeces to pulse indeces
                keys (tuple[int]): qubit indedes
                values (int): pulse indeces for self.pulse
            rho (dict): properties of systems
                rho['numQ']: number of qubits
                rho['rhoIni'] (numpy.ndarray): initial reduced density matrix
                rho['omegaQ'] (list): list of qubit frequency                
            bath (list): list of bath name
            V (numpy.ndarray): 3d array of system-bath coupling
                V[j, :, :]: system operator coupled with j th bath
            dtFB (float): step width for forward + backward time integration
            stride (int): loops per output
            isRK13 (bool): Runge-Kutta method
                True: 13-stage 5th-order Runge-Kutta
                False: 5-stage 4th-order Runge-Kutta
    """

    nu = []
    coeff = []
    depth = []
    bondDim = 0
    for i in range(rho['numQ']):
        nuTmp, coeffTmp, depthTmp, bondDimTmp, isRK13Tmp = \
            getBathParams(bath[i])
        
        nu.append(nuTmp)
        coeff.append(coeffTmp)
        depth.append(depthTmp)
        bondDim = max(bondDim, bondDimTmp)
        isRK13 = isRK13 or isRK13Tmp
    
    if rho['numQ'] == 1:
        TTs = TTs1Q(rho['rhoIni'], bondDim, V, depth, nu, coeff, pulse, map)
    elif rho['numQ'] == 2:
        TTs = TTs2QId(rho['rhoIni'], bondDim, V, depth, nu, coeff, pulse, map)
    
    setPulseSeq(qc, TTs, rho['omegaQ'], dtFB, idlingTime)
    timeEvo = timeEvolution(TTs, 0.5*dtFB, isRK13)

    with open(fileName, 'w') as file:
        currentTime = 0.0
        outputCurrentStates(currentTime, TTs, file)

        calcDynamics(dtFB, stride, TTs, timeEvo, file)

# 2qubit case, H+CNOT sequence
   
def get_result(**kwargs):

    s, T, kappa, omega_c = kwargs['s'], kwargs['T'], kwargs['kappa'], kwargs['omega_c']
    if [s, T, kappa, omega_c] == [1., 5., 0.004, 50.]:
        bath_id = 's=1'
    if [s, T, kappa, omega_c] == [1/2, 5., 0.004, 50.]:
        bath_id = 's=2'
    if [s, T, kappa, omega_c] == [1/8, 5., 0.004, 50.]:
        bath_id = 's=8'
    
    rho = {'numQ': kwargs['numQ']}
    rho['rhoIni'] = kwargs['init_state']
    sequence = []
    
    # Ry1(-pi/2) x Rx2(pi/2)
    paramsTmp = dict()
    paramsTmp['amp'] = [10*np.pi, 10*np.pi]
    paramsTmp['phase'] = [-np.pi/2, 0.0]
    paramsTmp['omega'] = [1.0, 1.0]
    paramsTmp['omegaQ'] = [1.0, 1.0]
    paramsTmp['J'] = [0.0]
    paramsTmp['time'] = np.pi / 2 / paramsTmp['amp'][0]
    
    sequence.append(paramsTmp)
    
    # # iSWAP
    paramsTmp = dict()
    paramsTmp['amp'] = [0.0, 0.0]
    paramsTmp['phase'] = [0.0, 0.0]
    paramsTmp['omega'] = [0.0, 0.0]
    paramsTmp['omegaQ'] = [1.0, 1.0]
    paramsTmp['J'] = [10*np.pi]
    paramsTmp['time'] = 3 * np.pi / 2 / paramsTmp['J'][0]
    
    sequence.append(paramsTmp)
    
    # # Ry1(-pi/2)
    paramsTmp = dict()
    paramsTmp['amp'] = [10*np.pi, 0.0]
    paramsTmp['phase'] = [-np.pi/2, 0.0]
    paramsTmp['omega'] = [1.0, 0.0]
    paramsTmp['omegaQ'] = [1.0, 1.0]
    paramsTmp['J'] = [0.0]
    paramsTmp['time'] = np.pi / 2 / paramsTmp['amp'][0]
    
    sequence.append(paramsTmp)
    
    # # iSWAP
    paramsTmp = dict()
    paramsTmp['amp'] = [0.0, 0.0]
    paramsTmp['phase'] = [0.0, 0.0]
    paramsTmp['omega'] = [0.0, 0.0]
    paramsTmp['omegaQ'] = [1.0, 1.0]
    paramsTmp['J'] = [10*np.pi]
    paramsTmp['time'] = 3 * np.pi / 2 / paramsTmp['J'][0]
    
    sequence.append(paramsTmp)
    
    bath = [bath_id, bath_id]
    
    V = np.array([[[0.0, 1.0],
                  [1.0, 0.0]],
    
                  [[0.0, 1.0],
                  [1.0, 0.0]]],
                 dtype=np.complex128)
    
    dtFB = kwargs['dtFB'] # 1e-3
    strideTime = 1e-2
    stride = int(strideTime // dtFB)
    
    result = main(rho, sequence, bath, V, dtFB, stride)

    # output density matrix
    # out = pd.DataFrame(np.zeros([result.shape[0], 33], dtype=np.float64))
    # out.iloc[:, 0] = result.iloc[:, 0]
    # out.iloc[:, 1::2] = result.iloc[:, 1:].values.real
    # out.iloc[:, 2::2] = result.iloc[:, 1:].values.imag
    # out.to_csv('data', sep=' ', header=None, index=False)
    return result

if __name__ == '__main__':
    # 2qubit case, H+CNOT sequence

    rho0=np.array([[1, 0, 0, 0],
              [0, 0, 0, 0],
              [0, 0, 0, 0],
              [0, 0, 0, 0]], dtype=np.complex128)
    result = get_result(numQ=2, s=1, T=5, kappa=0.004, omega_c=50, init_state=rho0, dtFB=1e-3)

    # display figure
    fig, axes = plt.subplots(4, 4, figsize=(8, 8))
    for i, ax in enumerate(axes.flatten()):
        ax.plot(result[0], result[i+1].values.real)
        ax.plot(result[0], result[i+1].values.imag)

    plt.show()