import customtkinter as ctk
import numpy as np
import scipy.constants as c

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
        self.T1_time_entry.insert(0, 250)
        self.T1_time_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # temperature label and entry
        self.temperature_label = ctk.CTkLabel(self, text="Temperature (mK):")
        self.temperature_label.grid(row=row, column=0, padx=10, pady=10)
        self.temperature_entry = ctk.CTkEntry(self)
        self.temperature_entry.insert(0, 1.5)
        self.temperature_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # exponent label and entry
        self.exponent_label = ctk.CTkLabel(self, text="Exponent:") 
        self.exponent_label.grid(row=row, column=0, padx=10, pady=10)
        self.exponent_entry = ctk.CTkEntry(self)
        self.exponent_entry.insert(0, "1")
        self.exponent_entry.grid(row=row, column=1, padx=10, pady=10)
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

        # depth label and integer entry
        self.depth_label = ctk.CTkLabel(self, text="Depth:")
        self.depth_label.grid(row=row, column=0, padx=10, pady=10)
        self.depth_entry = ctk.CTkEntry(self)   
        self.depth_entry.insert(0, 2)
        self.depth_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # bond dimension label and integer entry
        self.bondDim_label = ctk.CTkLabel(self, text="Bond dimension:")
        self.bondDim_label.grid(row=row, column=0, padx=10, pady=10)
        self.bondDim_entry = ctk.CTkEntry(self)
        self.bondDim_entry.insert(0, 20)
        self.bondDim_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # Use RF+ checkbox
        self.useRFPlus_var = ctk.BooleanVar(value=False)
        self.useRFPlus_checkbox = ctk.CTkCheckBox(self, text="Use RF+", variable=self.useRFPlus_var)
        self.useRFPlus_checkbox.grid(row=row, column=0, columnspan=2, padx=10, pady=10)
        row += 1

        # RK13 checkbox
        self.RK13_var = ctk.BooleanVar(value=False)
        self.RK13_checkbox = ctk.CTkCheckBox(self, text="Use RK13", variable=self.RK13_var)
        self.RK13_checkbox.grid(row=row, column=0, columnspan=2, padx=10, pady=10)
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
        T = float(self.temperature_entry.get())

        beta = c.hbar * self.master.kwargs['omegaQ'][0] * 1e9 / (T * 1e-3 * c.k)  # convert mK to K and use eV
        T1 = float(self.T1_time_entry.get())
        kappa = 1 / (self.master.kwargs['omegaQ'][0] * T1 * 2 * np.pi)
        exp = float(self.exponent_entry.get())

        bathParams = {'type': 'broadband', 'exp': exp, 'beta': beta, 'kappa': kappa, 'omegaC': 50.}
        return {
            'bath': [bathParams] * self.master.num_qubits,
            'strideTime': float(self.timestep_entry.get()),
            'dtFB': float(self.dtFB_entry.get()),
            'gate_time': float(self.gate_time_entry.get()),
            'idlingTime': float(self.idling_time_entry.get()),
            'depth': [int(self.depth_entry.get())] * self.master.num_qubits,
            'bondDim': int(self.bondDim_entry.get()),
            'useRFPlus': self.useRFPlus_var.get(),
            'isRK13': self.RK13_var.get(),
        }

    def change_state(self, state):
        change_state_all_widgets(self, state=state)
        self.continue_button.configure(state=state)

# ----------------------------------------------------------------------
