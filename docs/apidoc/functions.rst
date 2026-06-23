Top-level Functions
===================

This section documents the public functions available at the top level of the
``ttheom`` namespace (i.e., importable directly via ``from ttheom import ...``).

High-level simulation interface
--------------------------------

.. currentmodule:: ttheom.main

.. autofunction:: calcTimeEvo
.. autofunction:: main

Physical-unit helpers
----------------------

.. currentmodule:: ttheom.main

.. autofunction:: prepareSystemArgs
.. autofunction:: prepareBathArgs
.. autofunction:: prepareGateArgs

Bath decomposition
------------------

.. currentmodule:: ttheom.bath

.. autofunction:: getBathParams
.. autofunction:: broadbandNoise

Evaluation and analysis
-----------------------

.. currentmodule:: ttheom.evaluation

.. autofunction:: loadResult
.. autofunction:: getFidelity
.. autofunction:: getConcurrence
.. autofunction:: getLogarithmicNegativity
.. autofunction:: plotPulseSeq
