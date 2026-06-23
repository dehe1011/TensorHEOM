import sys
import io
import customtkinter as ctk
import qiskit.qpy as qpy
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ..gui_utils import PAD_OUTER, PAD_Y

# ----------------------------------------------------------------------


class CircuitEditor(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Quantum Circuit Editor")
        self.geometry("540x680")
        self.minsize(480, 580)
        self.master = master
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)   # draw_frame expands

        # ── instruction ──────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="Define your Qiskit circuit in the editor below.\n"
                 "The variable must be named  qc.",
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w",
        ).grid(row=0, column=0, padx=PAD_OUTER, pady=(PAD_OUTER, 4), sticky="w")

        # ── code editor ──────────────────────────────────────────────────
        self.code_box = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Courier New", size=12),
            wrap="none",
            height=160,
        )
        self.code_box.grid(
            row=1, column=0, padx=PAD_OUTER, pady=(0, 4), sticky="ew"
        )
        default_code = (
            "from qiskit import QuantumCircuit\n"
            "from qiskit.circuit.random import random_circuit\n"
            "\n"
            f"# qc = QuantumCircuit({master.numQ})\n"
            f"qc = random_circuit(num_qubits={master.numQ}, depth=3, max_operands=2)\n"
        )
        self.code_box.insert("1.0", default_code)

        # ── run button ───────────────────────────────────────────────────
        self.run_button = ctk.CTkButton(
            self,
            text="Build & Save Circuit",
            width=200,
            command=self._build_circuit,
        )
        self.run_button.grid(row=2, column=0, pady=(0, 4))

        # ── status box ───────────────────────────────────────────────────
        self.status_box = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Courier New", size=11),
            height=36,
            state="disabled",
        )
        self.status_box.grid(
            row=3, column=0, padx=PAD_OUTER, pady=(0, 4), sticky="ew"
        )

        # ── circuit diagram ───────────────────────────────────────────────
        self.draw_frame = ctk.CTkFrame(self)
        self.draw_frame.grid(
            row=4, column=0, padx=PAD_OUTER, pady=(0, PAD_OUTER),
            sticky="nsew",
        )

    # ------------------------------------------------------------------

    def _build_circuit(self):
        user_code = self.code_box.get("1.0", "end-1c")
        old_out, old_err = sys.stdout, sys.stderr
        buf_out, buf_err = io.StringIO(), io.StringIO()
        sys.stdout, sys.stderr = buf_out, buf_err

        try:
            local_env = {}
            exec(user_code, {}, local_env)   # nosec
            self.master.qc = local_env["qc"]

            with open(self.master.qcFilePath + ".qpy", "wb") as f:
                qpy.dump(self.master.qc, f)

            self._set_status(
                f"✓ Circuit saved to {self.master.qcFilePath}.qpy", ok=True
            )

            for w in self.draw_frame.winfo_children():
                w.destroy()
            fig = self.master.qc.draw(output="mpl")
            canvas = FigureCanvasTkAgg(fig, master=self.draw_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as exc:
            self._set_status(f"✗ Error: {exc}", ok=False)
        finally:
            sys.stdout, sys.stderr = old_out, old_err

    def _set_status(self, msg: str, ok: bool = True):
        self.status_box.configure(state="normal")
        self.status_box.delete("1.0", "end")
        self.status_box.insert("end", msg)
        self.status_box.configure(state="disabled")

# ----------------------------------------------------------------------
