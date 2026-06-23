.. _quickstart:

**********
Quickstart
**********

This page shows the fastest path from installation to a working simulation.
TensorHEOM offers two levels of API: a **high-level interface** (``calcTimeEvo``) that handles
unit conversions internally, and a **low-level interface** (``main``) that gives full control
over all parameters.

.. contents:: On this page
   :local:
   :depth: 2

Installation
============

.. code-block:: bash

   pip install ttheom

High-level API: a single qubit
================================

The function :func:`ttheom.main.calcTimeEvo` accepts physical units (GHz, ns, mK, µs)
and performs all internal conversions.

.. code-block:: python

   from qiskit import QuantumCircuit
   from ttheom import calcTimeEvo

   # 1. Define the quantum circuit
   qc = QuantumCircuit(1)
   qc.rx(1.5708, 0)   # Rx(π/2)
   qc.delay(0, 0)
   qc.ry(1.5708, 0)   # Ry(π/2)
   qc.delay(0, 0)
   qc.ry(-1.5708, 0)  # Ry(-π/2)

   # 2. Run the simulation
   calcTimeEvo(
       fileName="result_1q",
       qc=qc,
       numQ=1,
       freqQ=[5.0],      # qubit frequency in GHz
       gateTime=[16.0],  # single-qubit gate time in ns
       rhoIni=[[1, 0],
               [0, 0]],  # initial state |0><0|
       idlingTime=1.0,   # idling time between gates in ns
       T=30,             # temperature in mK
       T1=32,            # energy relaxation time in µs
       omegaC=20,        # bath cutoff frequency
       exp=1,            # spectral density exponent
       tol=1e-4,         # AAA decomposition tolerance
       dtFB=3.0,         # time step in ps
       depth=[1],        # FP-HEOM hierarchy depth
       bondDim=5,        # maximum MPS bond dimension
       strideTime=0.1,   # output interval in ns
   )

The output is written to ``result_1q.csv``.

High-level API: a two-qubit Bell state
=========================================

For a two-qubit circuit, set ``numQ=2`` and provide gate times for the
single-qubit gates followed by the two-qubit coupling gate:

.. code-block:: python

   from qiskit import QuantumCircuit
   from ttheom import calcTimeEvo

   # Bell state: H ⊗ I followed by CNOT
   qc = QuantumCircuit(2)
   qc.h(0)
   qc.cx(0, 1)

   calcTimeEvo(
       fileName="result_bell",
       qc=qc,
       numQ=2,
       freqQ=[5.0, 5.0],          # GHz
       gateTime=[16.0, 16.0, 50], # two 1Q gates + one 2Q gate, ns
       rhoIni=[[1, 0, 0, 0],
               [0, 0, 0, 0],
               [0, 0, 0, 0],
               [0, 0, 0, 0]],     # |00><00|
       idlingTime=1.0,             # ns
       T=30,                       # mK
       T1=32,                      # µs
       omegaC=20,
       exp=1,
       tol=1e-4,
       dtFB=3.0,                   # ps
       depth=[1, 1],               # one depth per qubit
       bondDim=5,
       strideTime=0.1,             # ns
   )

Reading and analysing results
==============================

The CSV output contains the time-evolved reduced density matrix.
TensorHEOM provides helper functions to load and analyse it:

.. code-block:: python

   from ttheom import loadResult, getFidelity, getConcurrence

   # Load results
   times, rhos = loadResult("result_bell.csv")

   # Gate fidelity with respect to the ideal Bell state
   import numpy as np
   rho_ideal = np.array([[0.5, 0, 0, 0.5],
                          [0,   0, 0, 0  ],
                          [0,   0, 0, 0  ],
                          [0.5, 0, 0, 0.5]])
   fidelities = [getFidelity(rho_ideal, rho) for rho in rhos]

   # Concurrence (entanglement measure)
   concurrences = [getConcurrence(rho) for rho in rhos]

Visualising the pulse sequence
================================

.. code-block:: python

   from ttheom import plotPulseSeq

   # Plots the pulse envelope of the compiled pulse sequence
   plotPulseSeq(fileName="result_bell.csv")

Understanding the parameters
=============================

System parameters
-----------------

``numQ``
    Number of qubits.

``freqQ``
    Qubit transition frequencies in GHz.

``rhoIni``
    Initial density matrix as a 2D list or NumPy array of shape
    ``(2**numQ, 2**numQ)``.

``idlingTime``
    Time between gates in ns.

``gateTime``
    Gate durations: the first ``numQ`` values are single-qubit gate times, the
    next ``numQ-1`` values are two-qubit gate times, all in ns.

Bath parameters
---------------

``T``
    Temperature in mK. Can be a scalar (same for all qubits) or a list.

``T1``
    Energy-relaxation time in µs. Can be a scalar or a list.

``omegaC``
    Bath cutoff frequency (in units of the maximum qubit frequency).

``exp``
    Exponent of the spectral density (Ohmic: ``exp=1``).

``tol``
    Tolerance for the AAA bath-decomposition algorithm.
    Smaller values give a more accurate decomposition but require more poles.

Simulation parameters
---------------------

``dtFB``
    Time step for the forward/backward HEOM propagation in ps.
    Typical values: 1–10 ps. Use smaller values for faster/stronger baths.

``depth``
    FP-HEOM hierarchy depth per qubit (list of int).
    Increasing depth improves accuracy; ``[1]`` or ``[2]`` is usually sufficient.

``bondDim``
    Maximum MPS bond dimension.
    Larger values are more accurate but slower. For a single qubit, 5–20 is typical.

``strideTime``
    Time between successive output snapshots in ns.

``fileName``
    Base name of the output CSV file (without extension).

Next steps
==========

- For the low-level ``main`` API and direct control over internal parameters,
  see the :ref:`User Guide <guide>`.
- For the full list of classes and functions, see the :ref:`API documentation <apidoc>`.
- For running simulations on an HPC cluster, see
  :func:`ttheom.ssh.submitJob` and :func:`ttheom.ssh.downloadResult`.
