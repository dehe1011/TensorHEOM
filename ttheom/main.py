import os
import scipy.constants as c
import numpy as np

from .bath import getBathParams
from .pulse import setGates
from .tt import TTs1Q, TTs2QId, TTsMQChainId
from .circuit import setPulseSeq
from .dynamics import timeEvolution, outputCurrentStates, calcDynamics
from .ssh import saveQC, loadQC

def prepareBathArgs(rho, omegaQmax, T, T1, omegaC, exp, tol):
    """Convert physical bath parameters to the internal bath dictionary format.

    Parameters
    ----------
    rho : dict
        System dictionary; ``rho['numQ']`` gives the number of qubits.
    omegaQmax : float
        Maximum qubit angular frequency (GHz), used for unit conversion.
    T : float or list of float
        Temperature(s) in mK.
    T1 : float or list of float
        Energy-relaxation time(s) in µs.
    omegaC : float or list of float
        Bath cutoff frequency(ies).
    exp : float or list of float
        Spectral-density exponent(s).
    tol : float or list of float
        AAA tolerance(s) for the bath decomposition.

    Returns
    -------
    bath : list of dict
        List of bath parameter dictionaries, one per qubit.
    """

    if not isinstance(T, list) and not isinstance(T, np.ndarray):
        T = [T] * rho['numQ']
    if not isinstance(T1, list) and not isinstance(T1, np.ndarray):
        T1 = [T1] * rho['numQ']
    if not isinstance(omegaC, list) and not isinstance(omegaC, np.ndarray):
        omegaC = [omegaC] * rho['numQ']
    if not isinstance(exp, list) and not isinstance(exp, np.ndarray):
        exp = [exp] * rho['numQ']
    if not isinstance(tol, list) and not isinstance(tol, np.ndarray):
        tol = [tol] * rho['numQ']

    beta = c.hbar * omegaQmax * 1e9 / (np.array(T) * 1e-3 * c.k)
    kappa = 1 / (omegaQmax * 1e9 * np.array(T1) * 1e-6 * 2 * np.pi)
    bath = [{'type': 'broadband', 'beta': float(beta[i]), 'kappa': float(kappa[i]),
            'omegaC': omegaC[i], 'exp': exp[i], 'tol': tol[i]} for i in range(rho['numQ'])]

    return bath

def prepareGateArgs(rho, omegaQmax, gateTime):
    """Build the gate-list argument expected by :func:`setGates`.

    Parameters
    ----------
    rho : dict
        System dictionary with keys ``'numQ'`` and ``'omegaQ'``.
    omegaQmax : float
        Maximum qubit angular frequency used for unit conversion.
    gateTime : list of float
        Gate times in ns; first ``numQ`` entries are for single-qubit gates,
        the next ``numQ-1`` entries are for two-qubit coupling gates.

    Returns
    -------
    gateList : list
        List of ``[qubit_indices, gate_type, kwargs]`` entries.
    """
    gateList = []
    for i in range(rho['numQ']):
        kwargs1Q = {'omega': float(-rho['omegaQ'][i]), 'gateTime': float(omegaQmax * gateTime[i]) }
        gateList.append([[i], 'rxyStep', kwargs1Q])
    for i in range(rho['numQ']-1):
        kwargs2Q = {'gateTime': float(omegaQmax * gateTime[rho['numQ'] + i]) }
        gateList.append([[i, i+1], 'directCplStepVarJ', kwargs2Q])
    return gateList

def prepareSystemArgs(numQ, freqQ, rhoIni=None, idlingTime=None, gateTime=None):
    """Build the system dictionary and normalize qubit frequencies.

    Parameters
    ----------
    numQ : int
        Number of qubits.
    freqQ : list of float
        Qubit frequencies in GHz.
    rhoIni : numpy.ndarray, optional
        Initial density matrix of shape ``(2**numQ, 2**numQ)``.
        Defaults to the ground state ``|0><0|``.
    idlingTime : float, optional
        Idling time (unused; reserved for future use).
    gateTime : list of float, optional
        Gate times (unused; reserved for future use).

    Returns
    -------
    omegaQmax : float
        Maximum qubit angular frequency (rad/ns).
    rho : dict
        System dictionary with keys ``'numQ'``, ``'rhoIni'``, ``'omegaQ'``.
    """
    omegaQ = 2*np.pi*np.array(freqQ)
    omegaQmax = max(omegaQ)
    omegaQ /= omegaQmax
    if rhoIni is None:
        rhoIni = np.zeros((2**numQ, 2**numQ), dtype=np.complex128)
        rhoIni[0, 0] = 1
    else:
        rhoIni = np.array(rhoIni, dtype=np.complex128)
    rho = {'numQ': numQ, 'rhoIni': rhoIni, 'omegaQ': omegaQ.tolist()}
    return omegaQmax, rho

def prepareArgs(numQ, freqQ, gateTime, T, T1, omegaC, exp, tol, rhoIni, idlingTime, dtFB, depth, bondDim):
    """Assemble all internal arguments needed to build the TT structure.

    Parameters
    ----------
    numQ : int
        Number of qubits.
    freqQ : list of float
        Qubit frequencies in GHz.
    gateTime : list of float
        Gate times in ns.
    T : float or list of float
        Temperature(s) in mK.
    T1 : float or list of float
        Energy-relaxation time(s) in µs.
    omegaC : float or list of float
        Bath cutoff frequency(ies).
    exp : float or list of float
        Spectral-density exponent(s).
    tol : float or list of float
        AAA tolerance(s).
    rhoIni : numpy.ndarray
        Initial density matrix.
    idlingTime : float
        Idling time in ns.
    dtFB : float
        Integration time step in fs.
    depth : list of int
        FP-HEOM hierarchy depths.
    bondDim : int
        Maximum MPS bond dimension.

    Returns
    -------
    tuple
        ``(omegaQmax, rho, bondDim, V, depth, bath, gateList, dtFB, idlingTime)``
        in internal units ready for the TT constructors.
    """
    omegaQmax, rho = prepareSystemArgs(numQ, freqQ, rhoIni=rhoIni, idlingTime=idlingTime, gateTime=gateTime)
    gateList = prepareGateArgs(rho, omegaQmax, gateTime)
    bath = prepareBathArgs(rho, omegaQmax, T, T1, omegaC, exp, tol)

    dtFB *= omegaQmax * 1e-3
    idlingTime *= omegaQmax
    V = np.array([[[0, 1],[1, 0]] for _ in range(rho['numQ'])], dtype=np.complex128)
    args = omegaQmax, rho, bondDim, V, depth, bath, gateList, dtFB, idlingTime
    return args

def reverseBathArgs(omegaQmax, bath):
    """Convert internal bath parameters back to physical units.

    Parameters
    ----------
    omegaQmax : float
        Maximum qubit angular frequency (rad/ns).
    bath : list of dict
        List of internal bath parameter dictionaries.

    Returns
    -------
    T : numpy.ndarray
        Temperatures in mK.
    T1 : numpy.ndarray
        Energy-relaxation times in µs.
    omegaC : list
        Cutoff frequencies.
    exp : list
        Spectral-density exponents.
    tol : list
        AAA tolerances.
    """
    T = c.hbar * omegaQmax * 1e9 / (np.array([b['beta'] for b in bath]) * 1e-3 * c.k)
    T1 = 1 / (omegaQmax * 1e9 * np.array([b['kappa'] for b in bath]) * 1e-6 * 2 * np.pi)
    omegaC = [b['omegaC'] for b in bath]
    exp = [b['exp'] for b in bath]
    tol = [b['tol'] for b in bath]
    return T, T1, omegaC, exp, tol

def reverseGateArgs(rho, omegaQmax, gateList):
    """Convert internal gate times back to physical units (ns).

    Parameters
    ----------
    rho : dict
        System dictionary with key ``'numQ'``.
    omegaQmax : float
        Maximum qubit angular frequency (rad/ns).
    gateList : list
        Internal gate list produced by :func:`prepareGateArgs`.

    Returns
    -------
    gateTime : list of float
        Gate times in ns.
    """
    gateTime = [gateList[i][2]['gateTime']/omegaQmax for i in range(2*rho['numQ']-1) ]
    return gateTime

def reverseSystemArgs(omegaQmax, rho):
    """Convert internal system parameters back to physical units.

    Parameters
    ----------
    omegaQmax : float
        Maximum qubit angular frequency (rad/ns).
    rho : dict
        Internal system dictionary with keys ``'numQ'``, ``'omegaQ'``,
        ``'rhoReal'``, ``'rhoImag'``.

    Returns
    -------
    numQ : int
        Number of qubits.
    freqQ : list of float
        Qubit frequencies in GHz.
    rhoIni : numpy.ndarray
        Initial density matrix (complex).
    """
    numQ = rho['numQ']
    freQ = np.array(rho['omegaQ']) * omegaQmax / (2*np.pi)
    rhoIni = np.array(rho['rhoReal']) + 1j * np.array(rho['rhoImag'])
    return numQ, freQ.tolist(), rhoIni

def reverseArgs(omegaQmax, rho, bondDim, V, depth, bath, gateList, dtFB, idlingTime):
    """Convert all internal arguments back to user-facing physical units.

    Parameters
    ----------
    omegaQmax : float
        Maximum qubit angular frequency (rad/ns).
    rho : dict
        Internal system dictionary.
    bondDim : int
        MPS bond dimension.
    V : numpy.ndarray
        System-bath coupling operators (not returned).
    depth : list of int
        FP-HEOM hierarchy depths.
    bath : list of dict
        Internal bath parameter dictionaries.
    gateList : list
        Internal gate list.
    dtFB : float
        Internal integration time step.
    idlingTime : float
        Internal idling time.

    Returns
    -------
    tuple
        ``(numQ, freqQ, gateTime, T, T1, omegaC, exp, tol, rhoIni,
        idlingTime, dtFB, depth, bondDim)`` in physical units.
    """
    numQ, freqQ, rhoIni = reverseSystemArgs(omegaQmax, rho)
    T, T1, omegaC, exp, tol = reverseBathArgs(omegaQmax, bath)
    gateTime = reverseGateArgs(rho, omegaQmax, gateList)
    return numQ, freqQ, gateTime, T, T1, omegaC, exp, tol, rhoIni, idlingTime/omegaQmax, dtFB/(omegaQmax*1e-3), depth, bondDim

def getArgs(directory, fileName):
    """Load simulation arguments from a saved quantum-circuit file.

    Parameters
    ----------
    directory : str
        Directory containing the ``qpy`` file.
    fileName : str
        Base name of the file (without extension or ``qcData_`` prefix).

    Returns
    -------
    kwargs : dict
        Dictionary of keyword arguments ready to pass to
        :func:`prepareTTs` or :func:`calcTimeEvo`.
    """
    qcFilePath = os.path.join(os.getcwd(), directory, 'qcData_' + fileName + '.qpy')
    qc = loadQC(qcFilePath)
    metadata = qc.metadata
    omegaQmax, rho, bondDim, V, depth, bath, gateList, dtFB, idlingTime = metadata['omegaQmax'], metadata['rho'], metadata['bondDim'], None, metadata['depth'], metadata['bath'], metadata['gateList'], metadata['dtFB'], metadata['idlingTime']
    numQ, freqQ, gateTime, T, T1, omegaC, exp, tol, rhoIni, idlingTime, dtFB, depth, bondDim = reverseArgs(omegaQmax, rho, bondDim, V, depth, bath, gateList, dtFB, idlingTime)
    kwargs = {
        "directory": directory,
        "fileName": fileName,
        "numQ": numQ,
        "freqQ": freqQ, # GHz
        "gateTime": gateTime, # ns
        "T": T, # mK
        "T1": T1, # us
        "omegaC": omegaC,
        "exp": exp,
        "tol": tol,
        "idlingTime": idlingTime, # ns
        "dtFB": dtFB, # fs
        "depth": depth,
        "bondDim": bondDim,
        "strideTime": metadata['stride'] * metadata['dtFB']/ metadata['omegaQmax'], # ns
        "useRFPlus": metadata['useRFPlus'],
        "isRK13": metadata['isRK13'],
    }

    rho = metadata['rho']
    rhoIni = np.array(rho['rhoReal']) + 1j * np.array(rho['rhoImag'])
    rhoIni.reshape(2**rho['numQ'], 2**rho['numQ'])
    kwargs["rhoIni"] = rhoIni
    kwargs["qc"] = qc
    return kwargs

def prepareTTs(fileName, qc, numQ, freqQ, gateTime, T, T1, omegaC, exp, tol, rhoIni, idlingTime, dtFB, depth, bondDim, strideTime, useRFPlus=False, isRK13=False, directory=None):
    """Build and initialize the tensor-train data structures for a simulation.

    Parameters
    ----------
    fileName : str
        Base name for the output files.
    qc : qiskit.QuantumCircuit
        Quantum circuit to be simulated.
    numQ : int
        Number of qubits.
    freqQ : list of float
        Qubit frequencies in GHz.
    gateTime : list of float
        Gate times in ns.
    T : float or list of float
        Temperature(s) in mK.
    T1 : float or list of float
        Energy-relaxation time(s) in µs.
    omegaC : float or list of float
        Bath cutoff frequency(ies).
    exp : float or list of float
        Spectral-density exponent(s).
    tol : float or list of float
        AAA tolerance(s) for the bath decomposition.
    rhoIni : numpy.ndarray
        Initial density matrix of shape ``(2**numQ, 2**numQ)``.
    idlingTime : float
        Idling time in ns.
    dtFB : float
        Integration time step in fs.
    depth : list of int
        FP-HEOM hierarchy depths, one per qubit.
    bondDim : int
        Maximum MPS bond dimension.
    strideTime : float
        Time between successive outputs in ns.
    useRFPlus : bool, optional
        Use the Redfield+ method (``True``) instead of FP-HEOM (``False``).
        Default ``False``.
    isRK13 : bool, optional
        Use the 13-stage 5th-order Runge-Kutta scheme (``True``) instead of
        the 5-stage 4th-order scheme (``False``). Default ``False``.
    directory : str or None, optional
        Output directory. If ``None``, files are written to the current directory.

    Returns
    -------
    TTs : TTs.TTs
        Initialized MPS/MPO object with compiled pulse sequences.
    params : dict
        Simulation parameter dictionary (saved to the ``qpy`` file metadata).
    """
    print(directory)

    if useRFPlus:
        depth  = [1] * len(depth)

    stride = int(strideTime / (dtFB*1e-3))
    omegaQmax, rho, bondDim, V, depth, bath, gateList, dtFB, idlingTime = prepareArgs(numQ, freqQ, gateTime, T, T1, omegaC, exp, tol, rhoIni, idlingTime, dtFB, depth, bondDim)

    # set filepath and save qc data
    if directory is not None:
        os.makedirs(directory, exist_ok=True)
        qcFilePath = os.path.join(os.getcwd(), directory, 'qcData_' + fileName)
    else:
        qcFilePath = 'qcData_' + fileName
    params = saveQC(qcFilePath, omegaQmax, qc, idlingTime, gateList, rho, bath, V, dtFB, stride, depth, bondDim, isRK13=isRK13, useRFPlus=useRFPlus)
    print(f"Saved quantum circuit data to {qcFilePath}.")
    print(params)

    # Connecting quantum gates and pulse sequence
    pulse, pulseMap = setGates(gateList)

    # Decomposition of bath correlation functions
    nu = []
    coeff = []
    for i in range(rho['numQ']):
        nuTmp, coeffTmp = getBathParams(bath[i])

        nu.append(nuTmp)
        coeff.append(coeffTmp)

    # Initialize Tensor Train structure
    if rho['numQ'] == 1:
        TTs = TTs1Q(rho['rhoIni'], bondDim, V, depth, nu, coeff,
                    pulse, pulseMap)
    elif rho['numQ'] == 2:
        TTs = TTs2QId(rho['rhoIni'], bondDim, V, depth, nu, coeff,
                      pulse, pulseMap)
    elif rho['numQ'] >= 3:
        TTs = TTsMQChainId(rho['numQ'], rho['rhoIni'], bondDim, V, depth,
                           nu, coeff, pulse, pulseMap)
    else:
        raise ValueError(
            f"Invalid number of qubits: expected an integer ≥ 1, got {rho['numQ']}."
        )

    # Compilation qiskit qc into pulse sequence
    _ = setPulseSeq(qc, TTs, rho['omegaQ'], dtFB, idlingTime)

    return TTs, params

def calcTimeEvo(fileName, qc, numQ, freqQ, gateTime, T, T1, omegaC, exp, tol, rhoIni, idlingTime, dtFB, depth, bondDim, strideTime, useRFPlus=False, isRK13=False, directory=None):
    """Build the TT structure and run the full time evolution.

    Parameters
    ----------
    fileName : str
        Base name for the output CSV file.
    qc : qiskit.QuantumCircuit
        Quantum circuit to be simulated.
    numQ : int
        Number of qubits.
    freqQ : list of float
        Qubit frequencies in GHz.
    gateTime : list of float
        Gate times in ns.
    T : float or list of float
        Temperature(s) in mK.
    T1 : float or list of float
        Energy-relaxation time(s) in µs.
    omegaC : float or list of float
        Bath cutoff frequency(ies).
    exp : float or list of float
        Spectral-density exponent(s).
    tol : float or list of float
        AAA tolerance(s) for the bath decomposition.
    rhoIni : numpy.ndarray
        Initial density matrix of shape ``(2**numQ, 2**numQ)``.
    idlingTime : float
        Idling time in ns.
    dtFB : float
        Integration time step in fs.
    depth : list of int
        FP-HEOM hierarchy depths, one per qubit.
    bondDim : int
        Maximum MPS bond dimension.
    strideTime : float
        Time between successive outputs in ns.
    useRFPlus : bool, optional
        Use the Redfield+ method. Default ``False``.
    isRK13 : bool, optional
        Use the 13-stage Runge-Kutta scheme. Default ``False``.
    directory : str or None, optional
        Output directory. Default ``None`` (current directory).
    """

    # setup tensor trains
    TTs, params = prepareTTs(fileName, qc, numQ, freqQ, gateTime, T, T1, omegaC, exp, tol, rhoIni, idlingTime, dtFB, depth, bondDim, strideTime, useRFPlus=useRFPlus, isRK13=isRK13, directory=directory)

    dtFB = params['dtFB']
    stride = params['stride']
    isRK13 = params['isRK13']

    # set filepath and save qc data
    if directory is not None:
        os.makedirs(directory, exist_ok=True)
        csvFilePath = os.path.join(os.getcwd(), directory, fileName+'.csv')
    else:
        csvFilePath = fileName+'.csv'
    print(f"Saved result data to {csvFilePath}.")

    # Time evolution
    timeEvo = timeEvolution(TTs, 0.5*dtFB, isRK13)

    with open(csvFilePath, 'w', encoding='utf-8') as file:
        stepNum = 0
        outputCurrentStates(dtFB, stepNum, TTs, file)
        calcDynamics(dtFB, stride, TTs, timeEvo, file)

def main(fileName, qc, idlingTime, gateList, rho,
         bath, V, dtFB, stride, depth, bondDim, isRK13=False,
         useRFPlus=False):
    """Run the HEOM simulation using pre-assembled internal arguments.

    The reduced density operator time series is written to ``fileName``.

    Parameters
    ----------
    fileName : str
        Path to the output file.
    qc : qiskit.QuantumCircuit
        Quantum circuit to be simulated.
    idlingTime : float
        Idling time in units of ``omegaQ[0]``.
    gateList : list
        List of ``[qubit_indices, gate_type, kwargs]`` entries.
    rho : dict
        System dictionary with keys:

        ``'numQ'`` : int
            Number of qubits.
        ``'rhoIni'`` : numpy.ndarray
            Initial reduced density matrix.
        ``'omegaQ'`` : list of float
            Qubit frequencies normalized by the maximum.

    bath : list of dict
        Bath parameter dictionaries, one per qubit.
    V : numpy.ndarray
        3-D array of system-bath coupling operators;
        ``V[j]`` is the system operator coupled to the ``j``-th bath.
    dtFB : float
        Step width for forward + backward time integration.
    stride : int
        Number of integration steps between successive outputs.
    depth : list of int
        FP-HEOM hierarchy depths.
    bondDim : int
        Maximum MPS bond dimension.
    isRK13 : bool, optional
        Use the 13-stage 5th-order Runge-Kutta scheme (``True``) or the
        5-stage 4th-order scheme (``False``). Default ``False``.
    useRFPlus : bool, optional
        Use the Redfield+ method. Default ``False``.
    """

    if useRFPlus:
        depth  = [1] * len(depth)

    # Decomposition of bath correlation functions
    nu = []
    coeff = []
    for i in range(rho['numQ']):
        nuTmp, coeffTmp = getBathParams(bath[i])

        nu.append(nuTmp)
        coeff.append(coeffTmp)

    # Connecting quantum gates and pulse sequence
    pulse, pulseMap = setGates(gateList)

    # Initialize Tensor Train structure
    if rho['numQ'] == 1:
        TTs = TTs1Q(rho['rhoIni'], bondDim, V, depth, nu, coeff,
                    pulse, pulseMap)
    elif rho['numQ'] == 2:
        TTs = TTs2QId(rho['rhoIni'], bondDim, V, depth, nu, coeff,
                      pulse, pulseMap)
    elif rho['numQ'] >= 3:
        TTs = TTsMQChainId(rho['numQ'], rho['rhoIni'], bondDim, V, depth,
                           nu, coeff, pulse, pulseMap)
    else:
        raise ValueError(
            f"Invalid number of qubits: expected an integer ≥ 1, got {rho['numQ']}."
        )

    # Compilation qiskit qc into pulse sequence
    setPulseSeq(qc, TTs, rho['omegaQ'], dtFB, idlingTime)

    # Time evolution
    timeEvo = timeEvolution(TTs, 0.5*dtFB, isRK13)

    with open(fileName, 'w', encoding='utf-8') as file:
        stepNum = 0
        outputCurrentStates(dtFB, stepNum, TTs, file)
        calcDynamics(dtFB, stride, TTs, timeEvo, file)
