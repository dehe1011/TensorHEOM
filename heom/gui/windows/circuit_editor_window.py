import customtkinter as ctk
import sys
import io
import qiskit.qpy as qpy
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ----------------------------------------------------------------------

class CircuitEditor(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Quantum Circuit Editor")
        self.geometry("400x600")
        self.master = master

        # Instruction label
        label = ctk.CTkLabel(self, text="Please define your circuit below.")
        label.pack(pady=10)

        # Textbox for code
        self.code_box = ctk.CTkTextbox(self, width=400, height=200)
        self.code_box.pack(padx=10, pady=10)
        self.code_box.insert("1.0", "from qiskit import QuantumCircuit\n")
        self.code_box.insert("2.0", "from qiskit.circuit.random import random_circuit\n")
        self.code_box.insert("3.0", "\n")
        self.code_box.insert("4.0", f"# qc = QuantumCircuit({master.numQ})\n")
        self.code_box.insert("5.0", f"qc = random_circuit(num_qubits={master.numQ}, depth=3, max_operands=2)")

        # Run + Save button
        self.run_button = ctk.CTkButton(self, text="Build & Save Circuit", command=self.build_circuit)
        self.run_button.pack(pady=10)

        # Output box
        self.output_box = ctk.CTkTextbox(self, width=400, height=20)
        self.output_box.pack(padx=10, pady=10)

        # Frame for drawing circuit
        self.draw_frame = ctk.CTkFrame(self, width=400, height=280)
        self.draw_frame.pack(padx=10, pady=10, fill="both", expand=True)

    def build_circuit(self):
        user_code = self.code_box.get("1.0", "end-1c")

        # Redirect stdout/stderr
        old_stdout, old_stderr = sys.stdout, sys.stderr
        redirected_output = sys.stdout = io.StringIO()
        redirected_error = sys.stderr = io.StringIO()

        try:
            local_env = {}
            exec(user_code, {}, local_env)
            self.master.qc = local_env["qc"]

            # Clear old drawing in frame
            for widget in self.draw_frame.winfo_children():
                widget.destroy()

            # save qc 
            with open(self.master.qcFilePath+'.qpy', 'wb') as file:
                qpy.dump(self.master.qc, file)
            print(f"Circuit built successfully and saved as {self.master.qcFilePath}")

            # Draw with matplotlib
            fig = self.master.qc.draw(output="mpl")
            canvas = FigureCanvasTkAgg(fig, master=self.draw_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            print(f"Error: {e}")

        # Restore stdout/stderr
        sys.stdout, sys.stderr = old_stdout, old_stderr
        output = redirected_output.getvalue() + redirected_error.getvalue()

        # Display output
        self.output_box.delete("1.0", "end")
        self.output_box.insert("end", output)

# ----------------------------------------------------------------------
