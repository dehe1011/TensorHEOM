Classes & Functions
===================

This section provides an overview of the available classes and functions contained in the `TensorHEOM` package.

Decomposition of bath auto-correlation functions
------------------------------------------------

.. currentmodule:: heom.bath

.. autofunction:: getBathParams
.. autofunction:: broadbandNoise

Connection of quantum gates and pulse sequences
-----------------------------------------------

.. currentmodule:: heom.pulse

.. autofunction:: setGates
.. autofunction:: getGate
.. autoclass:: directCplStepVarJ
.. autoclass:: iSwapDPulse
.. autoclass:: rxyStep
.. autoclass:: U3Pulse

Tensor Train representation
---------------------------

.. currentmodule:: heom.tt

.. autoclass:: TTs
.. autoclass:: TTsTwoLevelId
.. autoclass:: TTs1Q
.. autoclass:: TTs2QId
.. autoclass:: TTsMQChainId

Compilation of Qiskit circuits to pulse sequences
-------------------------------------------------

.. currentmodule:: heom.circuit

.. autofunction:: setPulseSeq
.. autofunction:: transform
.. autofunction:: scheduling

Time evolution
--------------

.. currentmodule:: heom.dynamics

.. autoclass:: timeEvolution
.. autofunction:: zRightOrth
.. autofunction:: calcDynamics
.. autofunction:: outputCurrentStates
.. autofunction::getRotatingRDO

Running Simulations on HPC 
--------------------------

.. currentmodule:: heom.ssh

.. autofunction::slurmShell # slurm.py
.. autofunction::slurmStatus # slurm.py
.. autofunction::commandsForSubmission # commands.py
.. autofunction::getStatus # commands.py
.. autofunction::getClient # connect_ssh.py
.. autofunction::submitJob # job_control.py
.. autofunction::downloadResult # job_control.py