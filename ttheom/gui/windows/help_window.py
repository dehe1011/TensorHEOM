import customtkinter as ctk

from ..gui_utils import PAD_OUTER

# ----------------------------------------------------------------------

_HELP_TEXT = """\
TensorHEOM — Help & Quick Reference
====================================

WORKFLOW OVERVIEW
-----------------
Step 1 · Circuit
  • Set the number of qubits and open the Circuit Editor to define your
    Qiskit circuit, or upload an existing .qpy file.
  • Click "Continue →" when the circuit is ready.

Step 2 · Parameters
  • Gates: enter qubit frequencies (GHz), idling time (ns), and gate
    durations for single-qubit (1Q) and two-qubit (2Q) gates (ns).
  • Bath: set the temperature (mK), T₁ relaxation time (µs), bath
    cutoff frequency, spectral exponent, and AAA tolerance.
  • Simulation: optionally edit the initial density matrix, then set the
    time step (ps), hierarchy depth, MPS bond dimension, and output
    interval (ns).
  • Click "Continue →" to proceed.

Step 3 · Run
  • "▶ Run Locally"  — runs the FP-HEOM simulation on your machine.
  • "Upload Result File" — loads a previously computed .csv result.
  • "Submit to HPC" / "Download Result" — submit to a SLURM cluster via
    SSH and retrieve the output once the job has finished.

Step 4 · Results
  • "Pulse Sequence" — visualise the compiled microwave pulse envelope.
  • "Calculate Fidelity" — gate fidelity with respect to the ideal unitary.
  • "Calculate Concurrence" — entanglement measure (2-qubit only).
  • "Plot" — open a plot of the reduced density matrix, fidelity, or
    concurrence versus time in a dedicated window.

KEY PARAMETERS
--------------
Hierarchy depth   — controls accuracy of the HEOM expansion.  Depth 1
                    is usually sufficient for weakly coupled baths.
Bond dimension    — maximum MPS bond dimension. Increase for stronger
                    inter-qubit correlations.
Time step (ps)    — integration step. Smaller values → more accurate
                    but slower.
RF+ (Redfield+)   — fast perturbative approximation; use for quick
                    checks with weak coupling.
RK13              — 13-stage 5th-order Runge-Kutta scheme; more stable
                    for stiff problems.

CIRCUIT EDITOR
--------------
The editor accepts any valid Qiskit Python snippet that defines a
variable named `qc` (QuantumCircuit). Example:

    from qiskit import QuantumCircuit
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

Click "Build & Save Circuit" to compile and preview the circuit diagram.

REFERENCES
----------
K. Nakamura & J. Ankerhold, Phys. Rev. B 111, 064503 (2025).
K. Nakamura & J. Ankerhold, arXiv:2510.05872 (2025).

Source code and documentation:
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
