import os
import qiskit.qpy as qpy

def saveQC(filePath, qc, idlingTime, gateList, rho, bath, V, dtFB, stride, depth, bondDim, isRK13=False, useRFPlus=False):

    # output parameters for simulation
    params = {}
    params['idlingTime'] = idlingTime
    params['gateList'] = gateList
    params['bath'] = bath
    params['dtFB'] = dtFB
    params['stride'] = stride
    params['depth'] = depth
    params['bondDim'] = bondDim
    params['isRK13'] = isRK13
    params['useRFPlus'] = useRFPlus
    
    rhoIni = rho.pop('rhoIni')
    rho['rhoReal'] = rhoIni.real.tolist()
    rho['rhoImag'] = rhoIni.imag.tolist()
    params['rho'] = rho
    
    VTmp = {}
    VTmp['real'] = V.real.tolist()
    VTmp['imag'] = V.imag.tolist()
    params['VTmp'] = VTmp
    
    qc.metadata = params
    
    with open(filePath, 'wb') as file:
        qpy.dump(qc, file)

def loadQC(directory, fileName):

    inputName = os.path.join(directory, 'qcData' + '_' + fileName)
    
    with open(inputName, 'rb') as file:
        qc = qpy.load(file)[0]

    return qc