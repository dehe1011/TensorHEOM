.. _guide:

**********
User Guide
**********

This guide explains TensorHEOM's workflow in depth.  It uses the **low-level
API** (:func:`ttheom.main.main`) to show explicitly how each layer of the
simulation — system, bath, pulse sequences, tensor-train structure, and time
evolution — fits together.  The :ref:`Quickstart <quickstart>` page covers the
high-level ``calcTimeEvo`` interface if you just want to run simulations
quickly.

.. contents:: On this page
   :local:
   :depth: 2

Overview
========

A TensorHEOM simulation proceeds in four steps:

1. **Define the quantum circuit** using Qiskit.
2. **Specify system and bath parameters** (frequencies, temperature, T1).
3. **Build pulse sequences and the tensor-train structure**.
4. **Run the time evolution** and save the reduced density matrix.

The diagram below shows how the package layers connect:

.. code-block:: text

   Qiskit circuit  ─┐
   System params   ─┤─▶  main() / calcTimeEvo()  ─▶  CSV results
   Bath params     ─┤       │
   Gate specs      ─┘    TensorHEOM internals:
                            ├─ pulse sequence compilation
                            ├─ bath AAA decomposition
                            ├─ TT structure construction
                            └─ TDVP / Runge-Kutta propagation

Example 1 — Single qubit with broadband noise
=============================================

This example simulates a single-qubit gate sequence under broadband Ohmic
noise using the low-level interface.

.. code-block:: python

   import numpy as np
   from qiskit import QuantumCircuit
   from ttheom.main import main

   # --- Quantum circuit ---
   qc = QuantumCircuit(1)
   qc.rx(0.5 * np.pi, 0)
   qc.delay(0, 0)
   qc.ry(0.5 * np.pi, 0)
   qc.delay(0, 0)
   qc.ry(-0.5 * np.pi, 0)

   # --- System dictionary (internal units) ---
   rho = {
       'numQ': 1,
       'rhoIni': np.array([[1, 0], [0, 0]], dtype=np.complex128),
       'omegaQ': [1.0],   # frequencies normalised to omegaQmax
   }

   # --- Gate specification ---
   # Each entry: [qubit_indices, gate_type, kwargs]
   kwargs1Q = {'omega': -rho['omegaQ'][0], 'gateTime': 0.1 * np.pi}
   gateList = [[[0], 'rxyStep', kwargs1Q]]

   # --- Bath parameters (internal units) ---
   bath = [{'type': 'broadband',
             'beta': 5,
             'kappa': 0.004 / (2 * np.pi),
             'omegaC': 50,
             'exp': 1,
             'tol': 1e-6}]

   # --- System-bath coupling operator ---
   V = np.array([[[0, 1], [1, 0]]], dtype=np.complex128)

   # --- Numerical parameters ---
   dtFB      = 0.001   # time step
   strideTime = 0.01
   stride    = int(strideTime / dtFB)
   depth     = [2]     # hierarchy depth
   bondDim   = 20      # MPS bond dimension

   # --- Run ---
   main('rdo_1qubit.csv', qc, 0.1, gateList, rho,
        bath, V, dtFB, stride, depth, bondDim)

The result is written to ``rdo_1qubit.csv``.

Understanding the internal units
---------------------------------

All frequencies are normalised to ``omegaQmax`` (the highest qubit frequency).
Time is measured in units of ``1/omegaQmax``.  The helper functions
:func:`ttheom.main.prepareSystemArgs`, :func:`ttheom.main.prepareBathArgs`, and
:func:`ttheom.main.prepareGateArgs` convert physical units (GHz, mK, µs, ns)
to internal units automatically.

Example 2 — Realistic single-qubit simulation (physical units)
===============================================================

This example uses the physical-unit helpers and closely matches the parameters
of a real superconducting-qubit device.

.. code-block:: python

   import numpy as np
   from qiskit import QuantumCircuit
   from ttheom.main import prepareSystemArgs, prepareBathArgs, prepareGateArgs, main

   qc = QuantumCircuit(1)
   qc.rx(0.5 * np.pi, 0)
   qc.delay(0, 0)
   qc.ry(0.5 * np.pi, 0)
   qc.delay(0, 0)
   qc.ry(-0.5 * np.pi, 0)

   # Physical-unit system parameters
   omegaQmax, rho = prepareSystemArgs(
       numQ=1,
       freqQ=[5.0],                              # GHz
       rhoIni=np.array([[1, 0], [0, 0]], dtype=np.complex128),
   )

   # Physical-unit bath parameters  (T=30 mK, T1=32 µs)
   bath = prepareBathArgs(rho, omegaQmax,
                          T=30, T1=32, omegaC=50, exp=1, tol=1e-6)

   # Gate list (gate time = 16 ns)
   gateList = prepareGateArgs(rho, omegaQmax, gateTime=[16.0])

   V = np.array([[[0, 1], [1, 0]]], dtype=np.complex128)

   dtFB_ns   = 0.005                     # ns
   dtFB      = dtFB_ns * omegaQmax       # internal units
   strideTime_ns = 3.0
   stride    = int(strideTime_ns / dtFB_ns)

   main('rdo_1qubit_realistic.csv', qc, 10 * np.pi, gateList, rho,
        bath, V, dtFB, stride, depth=[1], bondDim=5, useRFPlus=True)

The ``useRFPlus=True`` flag activates the Redfield+ method, which is a
computationally cheaper approximation suitable when the bath–system coupling
is weak.

Example 3 — Two-qubit Bell state
==================================

This example prepares a Bell state :math:`(|00\rangle + |11\rangle)/\sqrt{2}` using a Hadamard gate
followed by a CNOT, and simulates the entanglement dynamics under non-Markovian
noise.

.. code-block:: python

   import numpy as np
   from qiskit import QuantumCircuit
   from ttheom.main import prepareSystemArgs, prepareBathArgs, prepareGateArgs, main

   qc = QuantumCircuit(2)
   qc.h(0)
   qc.cx(0, 1)

   omegaQmax, rho = prepareSystemArgs(
       numQ=2,
       freqQ=[5.0, 5.0],
       rhoIni=np.array([[1, 0, 0, 0],
                         [0, 0, 0, 0],
                         [0, 0, 0, 0],
                         [0, 0, 0, 0]], dtype=np.complex128),
   )

   bath = prepareBathArgs(rho, omegaQmax,
                          T=30, T1=32, omegaC=50, exp=1, tol=1e-6)

   # Two single-qubit gates + one two-qubit gate
   gateList = prepareGateArgs(rho, omegaQmax, gateTime=[16.0, 16.0, 50.0])

   V = np.array([[[0, 1], [1, 0]],
                  [[0, 1], [1, 0]]], dtype=np.complex128)

   dtFB_ns = 0.001
   dtFB    = dtFB_ns * omegaQmax
   stride  = int(0.01 / dtFB_ns)

   main('rdo_bell.csv', qc, 0.1, gateList, rho,
        bath, V, dtFB, stride, depth=[2, 2], bondDim=20)

Analysing the results
======================

After a simulation has run, use the evaluation functions to inspect the output.

.. code-block:: python

   import numpy as np
   from ttheom import loadResult, getFidelity, getConcurrence, getLogarithmicNegativity

   times, rhos = loadResult('rdo_bell.csv')

   # Target Bell state
   bell = np.array([[0.5, 0, 0, 0.5],
                     [0,   0, 0, 0  ],
                     [0,   0, 0, 0  ],
                     [0.5, 0, 0, 0.5]])

   fidelities = [getFidelity(bell, rho) for rho in rhos]
   concurrences = [getConcurrence(rho) for rho in rhos]
   log_neg = [getLogarithmicNegativity(rho) for rho in rhos]

   print(f"Final fidelity:      {fidelities[-1]:.4f}")
   print(f"Final concurrence:   {concurrences[-1]:.4f}")
   print(f"Final log. neg.:     {log_neg[-1]:.4f}")

Bath decomposition
==================

The FP-HEOM method represents bath correlation functions as a sum of
exponentials.  TensorHEOM uses the AAA algorithm (via the ``baryrat`` library)
to decompose the bath spectral density automatically.

To inspect the decomposition:

.. code-block:: python

   from ttheom import getBathParams

   bath_params = {
       'type': 'broadband',
       'beta': 5,
       'kappa': 0.004 / (2 * np.pi),
       'omegaC': 50,
       'exp': 1,
       'tol': 1e-6,
   }

   z, d = getBathParams(bath_params)
   print("Poles  z:", z)
   print("Weights d:", d)

Each pole ``z[k]`` and weight ``d[k]`` represents one exponential in the
bath correlation function.  More poles give a more accurate representation.
The ``tol`` parameter controls how many poles are used.

Hierarchy depth and bond dimension
====================================

Two numerical parameters dominate accuracy and cost:

``depth``
    FP-HEOM hierarchy depth (per qubit).  Depth 1 includes first-order
    system–bath entanglement.  Depth 2 adds second-order corrections.
    Values above 3 are rarely needed for weakly coupled baths.

``bondDim``
    Maximum bond dimension of the MPS representation.
    Larger values capture more quantum correlations between qubits and bath
    modes.  For single-qubit simulations, 5–20 is typically sufficient;
    two-qubit simulations may need 20–100.

A good convergence check is to rerun the simulation with doubled ``depth``
and ``bondDim`` and verify that the output changes by less than your target
accuracy.

Redfield+ approximation
=========================

Setting ``useRFPlus=True`` activates the Redfield+ method, a perturbative
approximation that reduces computational cost significantly.  It is suitable
for weak coupling (large T1) and serves as a fast sanity check before
running a full FP-HEOM calculation.

HPC submission
==============

For long-running simulations, TensorHEOM can submit jobs to a SLURM cluster
and retrieve results automatically.  See :func:`ttheom.ssh.submitJob` and
:func:`ttheom.ssh.downloadResult` in the :ref:`API documentation <apidoc>`.

.. code-block:: python

   from ttheom import submitJob

   submission_params = {
       'hostname':    'cluster.example.org',
       'username':    'myuser',
       'password':    'mypassword',
       'otp':         '123456',
       'schedulerName': 'slurm',
       'numNodes':    1,
       'cpusPerTask': 16,
       'maxTime':     '0-04:00:00',
       'emailAddress': 'user@example.org',
       'others':      '#SBATCH --partition=normal',
       'venvPath':    '/home/myuser/.venv',
   }

   job_id = submitJob(submission_params, ...)
   print("Job submitted with ID:", job_id)
