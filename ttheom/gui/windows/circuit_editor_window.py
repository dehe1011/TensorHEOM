import sys
import io
from tkinter import messagebox

import customtkinter as ctk
import qiskit.qpy as qpy
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ..gui_utils import PAD_OUTER


class CircuitEditor(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Quantum Circuit Editor")
        self.geometry("400x400")
        self.minsize(450, 500)
        self.master = master

        # Track whether the circuit was successfully built and saved
        self._circuit_built = False
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.grid_columnconfigure(0, weight=1)

        # Editor and console get most space, preview stays compact
        self.grid_rowconfigure(1, weight=2)  # code editor
        self.grid_rowconfigure(4, weight=1)  # console
        self.grid_rowconfigure(6, weight=0)  # preview

        # ── instruction ──────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text=(
                "Define your Qiskit circuit below.\n"
                "The circuit variable must be named  qc."
            ),
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w",
        ).grid(
            row=0,
            column=0,
            padx=PAD_OUTER,
            pady=(PAD_OUTER, 6),
            sticky="w",
        )

        # ── code editor ──────────────────────────────────────────────────
        self.code_box = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Courier New", size=12),
            wrap="none",
            height=120,
        )
        self.code_box.grid(
            row=1,
            column=0,
            padx=PAD_OUTER,
            pady=(0, 8),
            sticky="nsew",
        )

        num_q = getattr(master, "numQ", 2)
        default_code = (
            "from qiskit import QuantumCircuit\n"
            "\n"
            f"qc = QuantumCircuit({num_q})\n"
            "qc.h(0)\n"
        )
        if num_q >= 2:
            default_code += "qc.cx(0, 1)\n"

        self.code_box.insert("1.0", default_code)

        # ── run button ───────────────────────────────────────────────────
        self.run_button = ctk.CTkButton(
            self,
            text="Build & Save Circuit",
            width=190,
            height=30,
            command=self._build_circuit,
        )
        self.run_button.grid(row=2, column=0, pady=(0, 8))

        # ── console label ────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="Console",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).grid(
            row=3,
            column=0,
            padx=PAD_OUTER,
            pady=(0, 2),
            sticky="w",
        )

        # ── console / status box ─────────────────────────────────────────
        self.console_box = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Courier New", size=11),
            height=60,
            wrap="word",
            state="disabled",
        )
        self.console_box.grid(
            row=4,
            column=0,
            padx=PAD_OUTER,
            pady=(0, 8),
            sticky="nsew",
        )

        # ── circuit preview label ────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="Circuit preview",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).grid(
            row=5,
            column=0,
            padx=PAD_OUTER,
            pady=(0, 2),
            sticky="w",
        )

        # ── circuit diagram ───────────────────────────────────────────────
        self.draw_frame = ctk.CTkFrame(self, height=140)
        self.draw_frame.grid(
            row=6,
            column=0,
            padx=PAD_OUTER,
            pady=(0, PAD_OUTER),
            sticky="ew",
        )
        self.draw_frame.grid_propagate(False)

    # ------------------------------------------------------------------

    def _build_circuit(self):
        user_code = self.code_box.get("1.0", "end-1c")

        old_out, old_err = sys.stdout, sys.stderr
        buf_out, buf_err = io.StringIO(), io.StringIO()
        sys.stdout, sys.stderr = buf_out, buf_err

        try:
            local_env = {}
            exec(user_code, {}, local_env)  # nosec

            if "qc" not in local_env:
                raise ValueError("No variable named `qc` was defined.")

            self.master.qc = local_env["qc"]

            with open(self.master.qcFilePath + ".qpy", "wb") as f:
                qpy.dump(self.master.qc, f)

            # Mark as successfully built only after saving succeeded
            self._circuit_built = True

            stdout_text = buf_out.getvalue().strip()
            stderr_text = buf_err.getvalue().strip()

            msg = f"✓ Circuit saved to:\n{self.master.qcFilePath}.qpy"
            if stdout_text:
                msg += f"\n\nstdout:\n{stdout_text}"
            if stderr_text:
                msg += f"\n\nstderr:\n{stderr_text}"

            self._set_console(msg)

            for widget in self.draw_frame.winfo_children():
                widget.destroy()

            fig = self.master.qc.draw(output="mpl")
            fig.set_size_inches(4.6, 1.5)

            canvas = FigureCanvasTkAgg(fig, master=self.draw_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as exc:
            stdout_text = buf_out.getvalue().strip()
            stderr_text = buf_err.getvalue().strip()

            msg = f"✗ Error:\n{exc}"
            if stdout_text:
                msg += f"\n\nstdout:\n{stdout_text}"
            if stderr_text:
                msg += f"\n\nstderr:\n{stderr_text}"

            self._set_console(msg)

        finally:
            sys.stdout, sys.stderr = old_out, old_err

    def _set_console(self, msg: str):
        self.console_box.configure(state="normal")
        self.console_box.delete("1.0", "end")
        self.console_box.insert("end", msg)
        self.console_box.configure(state="disabled")

    def _on_close(self):
        if not self._circuit_built:
            proceed = messagebox.askyesno(
                "Circuit not saved",
                "You have not built and saved the circuit yet.\n\n"
                "Do you really want to close the editor?",
                parent=self,
            )
            if not proceed:
                return

        self.destroy()