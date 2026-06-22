import customtkinter as ctk
import sys
import io

# ----------------------------------------------------------------------

class StateEditor(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Initial State Editor")
        self.geometry("400x500")
        self.master = master

        # Instruction label
        label = ctk.CTkLabel(self, text=f"Please define an initial density matrix for {master.numQ} below.")
        label.pack(pady=10)

        # Textbox for code
        self.code_box = ctk.CTkTextbox(self, width=400, height=200)
        self.code_box.pack(padx=10, pady=10)
        self.code_box.insert("1.0", "import numpy as np\n")
        self.code_box.insert("2.0", "\n")
        self.code_box.insert("3.0", f"init_state = np.array({self.master.kwargs['rhoIni']})\n")

        # Run + Save button
        self.run_button = ctk.CTkButton(self, text="Confirm", command=self.confirm)
        self.run_button.pack(pady=10)

        # Output box
        self.output_box = ctk.CTkTextbox(self, width=400, height=200)
        self.output_box.pack(padx=10, pady=10)


    def confirm(self):
        user_code = self.code_box.get("1.0", "end-1c")

        # Redirect stdout/stderr
        old_stdout, old_stderr = sys.stdout, sys.stderr
        redirected_output = sys.stdout = io.StringIO()
        redirected_error = sys.stderr = io.StringIO()

        try:
            local_env = {}
            exec(user_code, {}, local_env)
            self.master.kwargs['rhoIni'] = local_env["init_state"]

            print("Initial state built successfully.")
            print(self.master.kwargs['rhoIni'])

        except Exception as e:
            print(f"Error: {e}")

        # Restore stdout/stderr
        sys.stdout, sys.stderr = old_stdout, old_stderr
        output = redirected_output.getvalue() + redirected_error.getvalue()

        # Display output
        self.output_box.delete("1.0", "end")
        self.output_box.insert("end", output)

# ----------------------------------------------------------------------
