import os
import qiskit.qpy as qpy

def saveQC(filePath, omegaQmax, qc, idlingTime, gateList, rho, bath, V, dtFB, stride, depth, bondDim, isRK13=False, useRFPlus=False):

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
    
    rhoTmp = rho.copy()
    rhoIni = rhoTmp.pop('rhoIni')
    rhoTmp['rhoReal'] = rhoIni.real.tolist()
    rhoTmp['rhoImag'] = rhoIni.imag.tolist()
    params['rho'] = rhoTmp
    
    VTmp = {}
    VTmp['real'] = V.real.tolist()
    VTmp['imag'] = V.imag.tolist()
    params['VTmp'] = VTmp

    params['omegaQmax'] = omegaQmax
    
    qc.metadata = params
    
    with open(filePath+'.qpy', 'wb') as file:
        qpy.dump(qc, file)
    
    return params

def loadQC(qcFilePath):

    inputName = os.path.join(qcFilePath)
    
    with open(inputName, 'rb') as file:
        qc = qpy.load(file)[0]

    return qc