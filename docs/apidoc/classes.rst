Classes & Functions
===================

This section provides an overview of the available classes and functions contained in the `TensorHEOM` package.

Decomposition of bath auto-correlation functions
------------------------------------------------

.. currentmodule:: ttheom.bath

.. autofunction:: getBathParams
.. autofunction:: broadbandNoise

Connection of quantum gates and pulse sequences
-----------------------------------------------

.. currentmodule:: ttheom.pulse

.. autofunction:: setGates
.. autofunction:: getGate
.. autoclass:: directCplStepVarJ
.. autoclass:: iSwapDPulse
.. autoclass:: rxyStep
.. autoclass:: U3Pulse

Tensor Train representation
---------------------------

.. currentmodule:: ttheom.tt

.. autoclass:: TTs
.. autoclass:: TTsTwoLevelId
.. autoclass:: TTs1Q
.. autoclass:: TTs2QId
.. autoclass:: TTsMQChainId

Compilation of Qiskit circuits to pulse sequences
-------------------------------------------------

.. currentmodule:: ttheom.circuit

.. autofunction:: setPulseSeq
.. autofunction:: transform
.. autofunction:: scheduling

Time evolution
--------------

.. currentmodule:: ttheom.dynamics

.. autoclass:: timeEvolution
.. autofunction:: zRightOrth
.. autofunction:: calcDynamics
.. autofunction:: outputCurrentStates
.. autofunction:: getRotatingRDO

Running Simulations on HPC
--------------------------

.. currentmodule:: ttheom.ssh

.. autofunction:: slurmShell
.. autofunction:: slurmStatus
.. autofunction:: commandsForSubmission
.. autofunction:: getStatus
.. autofunction:: getClient
.. autofunction:: submitJob
.. autofunction:: downloadResult