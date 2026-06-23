.. figure:: figures/logo.png
   :align: center
   :width: 2.5in

TensorHEOM Documentation
=========================

**Version:** |release| | **License:** BSD 3-Clause | `GitHub <https://github.com/dehe1011/TensorHEOM>`_

TensorHEOM is a Python package for simulating quantum circuits in **non-Markovian environments**
using free-pole hierarchical equations of motion (FP-HEOM) combined with tensor-train (TT) compression.
It is designed for superconducting-qubit simulations and connects circuit-level `Qiskit <https://qiskit.org>`_
input with microscopic open-system dynamics.

.. figure:: figures/overview.png
   :align: center
   :width: 100%

Key Features
------------

- **Non-Markovian open-system dynamics** via free-pole HEOM (FP-HEOM)
- **Tensor-train (MPS/MPO) compression** for efficient multi-qubit simulations
- **Native Qiskit integration**: transpile and simulate arbitrary quantum circuits
- **Physical unit interface**: specify temperatures in mK, relaxation times T1 in µs, frequencies in GHz
- **Bath decomposition** via AAA algorithm (baryrat) for arbitrary spectral densities
- **Built-in analysis tools**: fidelity, concurrence, logarithmic negativity
- **HPC support**: submit and retrieve jobs on SLURM clusters via SSH
- **Graphical user interface** for interactive exploration

Quick Install
-------------

.. code-block:: bash

   pip install ttheom

For a full installation guide including editable installs and platform-specific
instructions see :doc:`installation`.

Minimal Example
---------------

.. code-block:: python

   from qiskit import QuantumCircuit
   from ttheom import calcTimeEvo

   qc = QuantumCircuit(1)
   qc.rx(1.5708, 0)   # Rx(π/2)

   calcTimeEvo(
       fileName="result",
       qc=qc,
       numQ=1,
       freqQ=[5.0],          # GHz
       gateTime=[16.0],      # ns
       T=30,                 # mK
       T1=32,                # µs
       omegaC=20,
       exp=1,
       tol=1e-4,
       rhoIni=[[1,0],[0,0]],
       idlingTime=1.0,       # ns
       dtFB=3.0,             # ps
       depth=[1],
       bondDim=5,
       strideTime=0.1,       # ns
   )

See :doc:`quickstart` for a step-by-step walkthrough with explanation of all parameters.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   guide/guide
   gui/gui

.. toctree::
   :maxdepth: 3
   :caption: API Reference

   apidoc/apidoc

.. toctree::
   :maxdepth: 1
   :caption: About

   biblio
   copyright

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
