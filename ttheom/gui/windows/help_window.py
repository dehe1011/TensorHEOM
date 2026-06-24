import customtkinter as ctk

from ..gui_utils import PAD_OUTER

# ----------------------------------------------------------------------

_HELP_TEXT = """\
TensorHEOM — Help & Quick Reference
====================================

TensorHEOM simulates quantum circuits under non-Markovian Gaussian noise
using FP-HEOM and tensor-train compression. The GUI follows the workflow
shown in the top navigation bar:

    1 · Circuit  →  2 · Parameters  →  3 · Run  →  4 · Results


STEP 1 · CIRCUIT
----------------
Number of qubits
  Choose the number of qubits in the circuit.

Open Circuit Editor
  Opens an editor where you can define a Qiskit circuit. The code must
  create a variable named `qc`.

  Example:
      from qiskit import QuantumCircuit
      qc = QuantumCircuit(2)
      qc.h(0)
      qc.cx(0, 1)

Upload Circuit (.qpy)
  Load a previously saved Qiskit circuit in QPY format.

Output
  Directory:
    Folder where the circuit, metadata, and simulation results are saved.

  Filename:
    Base name used for the generated files.

Continue →
  Proceeds to the parameter input.


STEP 2 · PARAMETERS
-------------------
Gates
  Qubit frequency (GHz):
    List of qubit frequencies, e.g. [5, 5].

  Idling time (ns):
    Optional idle time inserted after selected gates.

  1Q gate time (ns):
    Single-qubit X-gate time for each qubit, e.g. [16, 16].
    General single-qubit rotations are scaled according to their angle.

  2Q gate time (ns):
    Two-qubit gate time for each nearest-neighbor pair, e.g. [50].

Bath
  T1 relaxation time (us):
    Relaxation time used to set the system-bath coupling strength.

  Temperature (mK):
    Reservoir temperature.

  Cutoff frequency:
    Bath cutoff frequency in units of the reference qubit frequency.

  Spectral exponent:
    Determines the bath type.
      s = 1       Ohmic bath
      0 < s < 1   sub-Ohmic / 1/f-like bath

  AAA tolerance:
    Accuracy of the free-pole decomposition of the bath correlation
    function. Smaller values are more accurate but usually create more
    bath modes.

Simulation
  Initial state:
    Opens the state editor for the initial reduced density matrix.

  Time step (ps):
    Integration time step.

  Hierarchy depth:
    Maximum HEOM hierarchy depth for each reservoir.

  Bond dimension:
    Maximum tensor-train/MPS bond dimension.

  Output interval (ns):
    Time interval between saved reduced density matrices.


STEP 3 · RUN
------------
Run Locally
  Starts the tensor-train FP-HEOM simulation on the local machine.

Upload Result File
  Loads an existing CSV result file for analysis.

Submit to HPC
  Submits the simulation to a configured remote cluster.

Download Result
  Downloads the result file from the remote machine.

Back
  Returns to the parameter input.


STEP 4 · RESULTS
----------------
Pulse Sequence
  Plots the compiled pulse-level control sequence.

Calculate Fidelity
  Computes the fidelity with respect to the ideal isolated circuit
  evolution.

Calculate Concurrence
  Computes the concurrence for two-qubit simulations.

Plot Results
  Plots selected output quantities, such as the reduced density operator
  or computed figures of merit.


SAVED FILES
-----------
TensorHEOM saves the input circuit and simulation data automatically.

  qcData_<filename>.qpy
    Qiskit circuit in QPY format, including simulation metadata.

  <filename>.csv
    Simulation output. Complex-valued density-matrix elements are stored
    through real and imaginary parts.


PRACTICAL TIPS
--------------
Convergence
  First tighten the AAA tolerance, then increase the hierarchy depth.
  Finally refine the bond dimension and time step.

Difficult regimes
  Simulations become more expensive for low temperatures, strongly
  sub-Ohmic baths, strong system-bath coupling, many qubits, and long
  circuits.

Tensor-train bond dimension
  Increase this value if the dynamics are not converged or if stronger
  correlations are expected.

Hierarchy depth
  Depth 1 may be sufficient for weak coupling, but should always be
  checked for convergence.

Source code:
  https://github.com/dehe1011/TensorHEOM
"""

# ----------------------------------------------------------------------


class HelpWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Help — TensorHEOM")
        self.geometry("580x540")
        self.minsize(480, 400)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="Help & Quick Reference",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=0, column=0, padx=PAD_OUTER, pady=(PAD_OUTER, 4), sticky="w")

        tb = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Courier New", size=11),
            wrap="word",
            activate_scrollbars=True,
        )
        tb.grid(row=1, column=0, padx=PAD_OUTER, pady=(0, 4), sticky="nsew")
        tb.insert("1.0", _HELP_TEXT)
        tb.configure(state="disabled")

        ctk.CTkButton(
            self, text="Close", width=100, command=self.destroy
        ).grid(row=2, column=0, pady=(4, PAD_OUTER))

# ----------------------------------------------------------------------
