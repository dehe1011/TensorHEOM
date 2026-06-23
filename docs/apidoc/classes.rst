Classes & Module Functions
==========================

This section documents TensorHEOM's internal classes and module-level
functions, grouped by subsystem.

Pulse types and gate specifications
-------------------------------------

.. currentmodule:: ttheom.pulse

.. autofunction:: setGates
.. autofunction:: getGate
.. autoclass:: rxyStep
.. autoclass:: U3Pulse
.. autoclass:: iSwapDPulse
.. autoclass:: directCplStepVarJ

Tensor-train representation
----------------------------

.. currentmodule:: ttheom.tt

.. autoclass:: TTs
.. autoclass:: TTsTwoLevelId
.. autoclass:: TTs1Q
.. autoclass:: TTs2QId
.. autoclass:: TTsMQChainId

Circuit compilation
-------------------

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

HPC cluster support
--------------------

.. currentmodule:: ttheom.ssh

.. autofunction:: submitJob
.. autofunction:: downloadResult
.. autofunction:: getClient
.. autofunction:: commandsForSubmission
.. autofunction:: getStatus
.. autofunction:: slurmShell
.. autofunction:: slurmStatus
