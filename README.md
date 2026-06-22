<p align="center">
    <img src="docs/figures/logo.png" width="250">
</p>

<p align="center">
    <a href="https://opensource.org/licenses/BSD-3-Clause">
        <img src="https://img.shields.io/badge/license-New%20BSD-blue.svg"
            alt="License"></a>
    <a href='https://github.com/dehe1011/QuantumDNA/actions/workflows/code-quality.yml'>
        <img src='https://img.shields.io/github/actions/workflow/status/dehe1011/QuantumDNA/code-quality.yml?branch=main'
            alt='GitHub Workflow Status' /></a>
    <a href='https://github.com/psf/black'>
        <img src='https://img.shields.io/badge/code%20style-black-000000.svg'
            alt='Code Style: black' /></a>
</p>

---

# TensorHEOM

**Authors: Kiyoto Nakamura, Dennis Herb**

TensorHEOM is a Python package for simulating quantum circuits in non-Markovian environments using free-pole hierarchical equations of motion (FP-HEOM) and tensor-train (TT) compression.

The package is designed for superconducting-qubit simulations and connects circuit-level Qiskit input with microscopic open-system dynamics.

<p align="center">
    <img src="docs/figures/overview.png" width="800">
</p>

## Installation

Install TensorHEOM from PyPI with

```bash
pip install ttheom
```

## Basic usage

A typical workflow is:

1. Define a Qiskit quantum circuit.
2. Specify system, bath, and numerical parameters.
3. Run the TensorHEOM simulation.
4. Analyze the reduced density matrix, fidelity, and entanglement measures.

```python
from qiskit import QuantumCircuit
from ttheom import *calcTimeEvo*

system_kwargs = {
    "numQ": 1,
    "freqQ": [5], # GHz
    "rhoIni": np.array([[1,0],[0,0]]),
    "gateTime": [16], # ns
    "idlingTime": 1, # ns
}
omegaQmax, rho = prepareSystemArgs(**system_kwargs)

# set qc
qc = QuantumCircuit(1)
qc.rx(0.5*np.pi, 0)
qc.delay(0, 0)
qc.ry(0.5*np.pi, 0)
qc.delay(0, 0)
qc.ry(-0.5*np.pi, 0)
system_kwargs["qc"] = qc

# set bath params
bath_kwargs = {
    "T": 30, # mK
    "T1": 32, # us
    "omegaC": 20,
    "exp": 1,
    "tol": 1e-4,
}
bathParams = prepareBathArgs(rho, omegaQmax, **bath_kwargs)[0]

# AAA decomposition
z, d = getBathParams(bathParams)

# set simulations params
simulation_kwargs= {
    "directory": ...,
    "fileName": ...,
    "dtFB": 1.5, # ps
    "depth": [1],
    "bondDim": 5,
    "strideTime": 0.1, # ns
    "useRFPlus": False,
    "isRK13": False,
}

# run the calculation 
calcTimeEvo(**system_kwargs, **bath_kwargs, **simulation_kwargs) 
```

## Graphical interface

TensorHEOM also provides a graphical user interface:

```python
from ttheom import TensorHeomApp

TensorHeomApp().mainloop()
```

<p align="center">
    <img src="docs/figures/GUI1.png" width="800">
</p>

## Documentation and examples

Example scripts and workflows are provided in the repository and in the accompanying paper.

## References

Recent papers from our group:

* [K. Nakamura and J. Ankerhold, Impact of time-retarded noise on dynamical decoupling schemes for qubits. *Physical Review B* **111**, 064503 (2025).](https://doi.org/10.1103/PhysRevB.111.064503)
* [K. Nakamura and J. Ankerhold, Entanglement dynamics and performance of two-qubit gates for superconducting qubits under non-Markovian effects. *Physical Review Research* **8**, 013337 (2026).](https://doi.org/10.1103/b5jp-s6t2)

## License

TensorHEOM is distributed under the BSD 3-Clause License.

## Support

For questions or support, please contact Dennis Herb at dennis.herb@uni-ulm.de.

