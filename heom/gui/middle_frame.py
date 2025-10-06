import customtkinter as ctk

from .gui_utils import change_state_all_widgets

# ----------------------------------------------------------------------

class MiddleFrame(ctk.CTkFrame):
    def __init__(self, master):

        # initialization of the ctk.CTkFrame class
        super().__init__(master)
        row = 0

        # --------------------------------------------------------------

        # label
        self.logo_label = ctk.CTkLabel(
            self, text="System", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
        row += 1

        # qubit architecture combobox
        self.qubit_architecture_label = ctk.CTkLabel(self, text="Qubit architecture:")
        self.qubit_architecture_label.grid(row=row, column=0, padx=10, pady=10)

        self.qubit_architecture_combobox = ctk.CTkComboBox(
            self, values=["chain", "ladder"]
        )
        self.qubit_architecture_combobox.set("chain")
        self.qubit_architecture_combobox.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # qubit frequency label and entry
        self.qubit_frequency_label = ctk.CTkLabel(self, text="Qubit frequency (GHz):")
        self.qubit_frequency_label.grid(row=row, column=0, padx=10, pady=10)

        self.qubit_frequency_entry = ctk.CTkEntry(self)
        self.qubit_frequency_entry.insert(0, 1)
        self.qubit_frequency_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # empty row for spacing
        self.grid_rowconfigure(row, weight=1)
        row += 1

        # --------------------------------------------------------------

        # label
        self.logo_label = ctk.CTkLabel(
            self, text="Gates", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
        row += 1

        # Idling time label and entry
        self.idling_time_label = ctk.CTkLabel(self, text="Idling time (ns):")
        self.idling_time_label.grid(row=row, column=0, padx=10, pady=10)
        self.idling_time_entry = ctk.CTkEntry(self)
        self.idling_time_entry.insert(0, 0.1)
        self.idling_time_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # Gate time label and entry
        self.gate_time_label = ctk.CTkLabel(self, text="Gate time (ns):")
        self.gate_time_label.grid(row=row, column=0, padx=10, pady=10)
        self.gate_time_entry = ctk.CTkEntry(self)
        self.gate_time_entry.insert(0, 0.1)
        self.gate_time_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # empty row for spacing
        self.grid_rowconfigure(row, weight=1)
        row += 1

        # --------------------------------------------------------------

        # label
        self.logo_label = ctk.CTkLabel(
            self, text="Bath", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
        row += 1

        # T1 time label and entry
        self.T1_time_label = ctk.CTkLabel(self, text="T1 time (ns):")
        self.T1_time_label.grid(row=row, column=0, padx=10, pady=10)
        self.T1_time_entry = ctk.CTkEntry(self)
        self.T1_time_entry.insert(0, 0)
        self.T1_time_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # temperature label and entry
        self.temperature_label = ctk.CTkLabel(self, text="Temperature (K):")
        self.temperature_label.grid(row=row, column=0, padx=10, pady=10)
        self.temperature_entry = ctk.CTkEntry(self)
        self.temperature_entry.insert(0, 0)
        self.temperature_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # exponent combobox
        self.exponent_label = ctk.CTkLabel(self, text="Exponent:")
        self.exponent_label.grid(row=row, column=0, padx=10, pady=10)
        self.exponent_combobox = ctk.CTkComboBox(
            self, values=["s=1", "s=1/2", "s=1/8"]
        )
        self.exponent_combobox.set("s=1")
        self.exponent_combobox.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # empty row for spacing
        self.grid_rowconfigure(row, weight=1)
        row += 1

        # --------------------------------------------------------------

        # label
        self.logo_label2 = ctk.CTkLabel(
            self, text="Simulation", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label2.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
        row += 1

        # initial state label and button to open state editor
        self.initial_state_label = ctk.CTkLabel(self, text="Initial state:")
        self.initial_state_label.grid(row=row, column=0, padx=10, pady=10)
        self.initial_state_button = ctk.CTkButton(
            self, text="Open State Editor", command=master.open_state_editor
        )
        self.initial_state_button.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # dtFB label and entry
        self.dtFB_label = ctk.CTkLabel(self, text="dtFB (ns):")
        self.dtFB_label.grid(row=row, column=0, padx=10, pady=10)
        self.dtFB_entry = ctk.CTkEntry(self)
        self.dtFB_entry.insert(0, 0.001)
        self.dtFB_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # timestep label and entry
        self.timestep_label = ctk.CTkLabel(self, text="Timestep (ns):")
        self.timestep_label.grid(row=row, column=0, padx=10, pady=10)
        self.timestep_entry = ctk.CTkEntry(self)
        self.timestep_entry.insert(0, 0.01)
        self.timestep_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # RK13 checkbox
        self.RK13_var = ctk.BooleanVar(value=False)
        self.RK13_checkbox = ctk.CTkCheckBox(self, text="Use RK13", variable=self.RK13_var)
        self.RK13_checkbox.grid(row=row, column=0, columnspan=2, padx=10, pady=10)
        row += 1

        # HPC checkbox
        self.HPC_var = ctk.BooleanVar(value=False)
        self.HPC_checkbox = ctk.CTkCheckBox(self, text="Use HPC", variable=self.HPC_var)
        self.HPC_checkbox.grid(row=row, column=0, columnspan=2, padx=10, pady=10)
        row += 1

        # empty row for spacing
        self.grid_rowconfigure(row, weight=1)
        row += 1

        # --------------------------------------------------------------

        # confirm button
        self.continue_button = ctk.CTkButton(
            self, text="Continue", command=master.continue_to_right_frame
        )
        self.continue_button.grid(row=row, column=1, columnspan=1, pady=10, padx=10)

        # back button
        self.back_button = ctk.CTkButton(
            self, text="Back", command=master.back_to_left_frame
        )
        self.back_button.grid(row=row, column=0, columnspan=1, pady=10, padx=10)

    # ------------------------------------------------------------------

    def get_kwargs(self):
        return {
            'architecture': self.qubit_architecture_combobox.get(),
            'omegaQ': [float(self.qubit_frequency_entry.get())] * self.master.num_qubits,
            'bath': [self.exponent_combobox.get()] * self.master.num_qubits,
            'strideTime': float(self.timestep_entry.get()),
            'dtFB': float(self.dtFB_entry.get()),
            'gate_time': float(self.gate_time_entry.get()),
            'idlingTime': float(self.idling_time_entry.get()),
            'isRK13': self.RK13_var.get(),
            'useHPC': self.HPC_var.get(),
        }

    def change_state(self, state):
        change_state_all_widgets(self, state=state)
        self.continue_button.configure(state=state)

# ----------------------------------------------------------------------
