import json
import os
import numpy as np

from . import DATA_DIR

def getBathParams(bath):
    """return bath parameters

        params:
            bath (str): id for bath
        
        returns:
            nu (list): list of poles for FP-HEOM
            coeff (list): list of poles for FP-HEOM
            depth (int): depth of FP-HEOM
            bondDim (int): bond dimension of MPS
                isRK13 (bool): Runge-Kutta method
                    True: 13-stage 5th-order Runge-Kutta
                    False: 5-stage 4th-order Runge-Kutta
    """

    if bath == 's=1':
        jsonFile = open(os.path.join(DATA_DIR, 's1.json'), 'r')
    elif bath == 's=1/2':
        jsonFile = open(os.path.join(DATA_DIR, 's2.json'), 'r')
    elif bath == 's=1/8':
        jsonFile = open(os.path.join(DATA_DIR, 's8.json'), 'r')
        
    jsonDict = json.load(jsonFile)
    
    nu = np.array(jsonDict['nu_real']) + 1j * np.array(jsonDict['nu_imag'])
    coeff = np.array(jsonDict['coeff_real']) + 1j * np.array(jsonDict['coeff_imag'])

    return nu, coeff, jsonDict['depth'], jsonDict['bondDim'], jsonDict['isRK13']