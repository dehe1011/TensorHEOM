import importlib
import sys
import os
import numpy as np

def setGates(gateList: list) -> tuple[list, dict]:
    """create instances for qubit gates

        params:
            gateList (list): input list for qubit gates
                gateList[:][0] (list[int]): qubit index
                gateList[:][1] (str): gate name
                gateList[:][2] (dict): kwargs for gates

        returns:
            pulse (list): list with qubit index and pulse
            map (dict): dictionary for mapping
                from qubit indeces to pulse indeces
    """

    numGates = len(gateList)

    pulse = []
    map = {}

    for i in range(numGates):
        pulse.append([gateList[i][0],
                      getGate(gateList[i][1], gateList[i][2])])
        
        pulseIdx = tuple(np.sort([j for j in gateList[i][0]]))
        map[pulseIdx] = i

    return pulse, map

def getGate(pulseName: str, kwargs: dict):
    """create a instance for pulse

        params:
            pulseName (str): gate name
            kwargs (dict): arguments for pulse

        returns:
            abstract_pulse.abstractPulse: class for gate
    """

    sys.path.append(os.path.dirname(__file__))
    class_map = {
        'rxyStep': '.rxy_step',
        'directCplStepVarJ': '.direct_cpl_step_varJ',
    }

    if pulseName in class_map:
        module = importlib.import_module(class_map[pulseName],
                                         package=__package__)
        cls = getattr(module, pulseName)
    
    return cls(**kwargs)