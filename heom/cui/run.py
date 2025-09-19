from qiskit import qpy
import numpy as np
from ..main import main

def run(inputName: str, outputName: str):
    """run simulation using serialized file

        params:
            inputName (str): name of input file
                The file is in QPY format.

            outputName (str): name of output file
                Dynamics of reduced density matrices are stored
                in the CSV format in the file.
    """

    with open(inputName, 'rb') as file:
        qc = qpy.load(file)[0]

    params = qc.metadata
    idlingTime = params['idlingTime']
    gateList = params['gateList']
    rho = params['rho']
    rho['rhoIni'] = np.array(rho['rhoReal']) + 1j * np.array(rho['rhoImag'])
    bath = params['bath']
    VTmp = params['VTmp']
    V = np.array(VTmp['real']) + 1j * np.array(VTmp['imag'])
    dtFB = params['dtFB']
    stride = params['stride']
    isRK13 = params['isRK13']

    main(outputName, qc, idlingTime, gateList, rho,
         bath, V, dtFB, stride, isRK13)
