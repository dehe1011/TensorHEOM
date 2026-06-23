import importlib
import sys
import os
import numpy as np

def setGates(gateList: list) -> tuple[list, dict]:
    """Create pulse instances for all qubit gates in the gate list.

    Parameters
    ----------
    gateList : list
        Input list of gate specifications. Each element is a 3-item list:

        ``gateList[i][0]`` : list of int
            Qubit indices the gate acts on.
        ``gateList[i][1]`` : str
            Gate name (e.g. ``'rxyStep'``, ``'directCplStepVarJ'``).
        ``gateList[i][2]`` : dict
            Keyword arguments passed to the pulse constructor.

    Returns
    -------
    pulse : list
        List of ``[qubit_indices, pulse_instance]`` pairs.
    pulseMap : dict
        Mapping from sorted qubit-index tuples to pulse list indices.
    """

    numGates = len(gateList)

    pulse = []
    pulseMap = {}

    for i in range(numGates):
        pulse.append([gateList[i][0],
                      getGate(gateList[i][1], gateList[i][2])])

        pulseIdx = tuple(np.sort([j for j in gateList[i][0]]))
        pulseMap[pulseIdx] = i

    return pulse, pulseMap

def getGate(pulseName: str, kwargs: dict):
    """Instantiate a pulse object by name.

    Parameters
    ----------
    pulseName : str
        Name of the pulse class (e.g. ``'rxyStep'``).
    kwargs : dict
        Keyword arguments forwarded to the pulse constructor.

    Returns
    -------
    abstractPulse
        Instantiated pulse object.

    Raises
    ------
    ValueError
        If ``pulseName`` is not a supported gate type.
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

    else:
        raise ValueError(f"Unsupported gate type: {pulseName}")

    return cls(**kwargs)
