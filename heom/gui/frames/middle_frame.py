import customtkinter as ctk
import numpy as np
import scipy.constants as c
import ast

from ..gui_utils import change_state_all_widgets

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

        # qubit frequency label and entry
        self.qubit_frequency_label = ctk.CTkLabel(self, text="Qubit frequency (GHz):")
        self.qubit_frequency_label.grid(row=row, column=0, padx=10, pady=10)

        self.qubit_frequency_entry = ctk.CTkEntry(self)
        self.qubit_frequency_entry.insert(0, str([5] * self.master.num_qubits) ) # omegaQ_max = 5 * 2* np.pi
        self.qubit_frequency_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # Idling time label and entry
        self.idling_time_label = ctk.CTkLabel(self, text="Idling time (ns):")
        self.idling_time_label.grid(row=row, column=0, padx=10, pady=10)
        self.idling_time_entry = ctk.CTkEntry(self)
        self.idling_time_entry.insert(0, 1) # omegaQ_max * 1
        self.idling_time_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # Gate time label and entry
        self.gate_time_label = ctk.CTkLabel(self, text="Gate time (ns):")
        self.gate_time_label.grid(row=row, column=0, padx=10, pady=10)
        self.gate_time_entry = ctk.CTkEntry(self)
        self.gate_time_entry.insert(0, str([16] * self.master.num_qubits)) # omegaQ_max * 16
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
        self.T1_time_label = ctk.CTkLabel(self, text="T1 time (us):")
        self.T1_time_label.grid(row=row, column=0, padx=10, pady=10)
        self.T1_time_entry = ctk.CTkEntry(self)
        self.T1_time_entry.insert(0, 32) # kappa/(2*np.pi) = 1 / (omegaQ_max * 1e9 * 32 * 1e-6 * 2*np.pi) 
        self.T1_time_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # temperature label and entry
        self.temperature_label = ctk.CTkLabel(self, text="Temperature (mK):")
        self.temperature_label.grid(row=row, column=0, padx=10, pady=10)
        self.temperature_entry = ctk.CTkEntry(self)
        self.temperature_entry.insert(0, 30) # beta = c.hbar * omegaQ_max * 1e9 / (30 * 1e-3 * c.k)
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
        self.dtFB_label = ctk.CTkLabel(self, text="Simulation step:")
        self.dtFB_label.grid(row=row, column=0, padx=10, pady=10)
        self.dtFB_entry = ctk.CTkEntry(self)
        self.dtFB_entry.insert(0, 0.005) # 1
        self.dtFB_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # timestep label and entry
        self.stride_time_label = ctk.CTkLabel(self, text="Timestep:")
        self.stride_time_label.grid(row=row, column=0, padx=10, pady=10)
        self.stride_time_entry = ctk.CTkEntry(self)
        self.stride_time_entry.insert(0, 3)
        self.stride_time_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # depth label and integer entry
        self.depth_label = ctk.CTkLabel(self, text="Depth:")
        self.depth_label.grid(row=row, column=0, padx=10, pady=10)
        self.depth_entry = ctk.CTkEntry(self)   
        self.depth_entry.insert(0, 1)
        self.depth_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # bond dimension label and integer entry
        self.bondDim_label = ctk.CTkLabel(self, text="Bond dimension:")
        self.bondDim_label.grid(row=row, column=0, padx=10, pady=10)
        self.bondDim_entry = ctk.CTkEntry(self)
        self.bondDim_entry.insert(0, 5)
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

        # omegaQ = 1 -> input: 1/(2*np.pi)
        # gateTime = 0.1*np.pi -> input 

        omegaQ_list = ast.literal_eval(self.qubit_frequency_entry.get())
        omegaQ_list = np.array(omegaQ_list) * 2 * np.pi  # convert to angular frequency
        omegaQ_max = max(omegaQ_list)
        omegaQ_list = np.array(omegaQ_list) / omegaQ_max

        gate_time_list = ast.literal_eval(self.gate_time_entry.get()) 
        gate_time_list = np.array(gate_time_list) * omegaQ_max # convert to units of omegaQ_max
        idling_time = float(self.idling_time_entry.get()) * omegaQ_max
    
        # bath parameters
        T = float(self.temperature_entry.get())
        T1 = float(self.T1_time_entry.get())
        exp = float(self.exponent_entry.get())
        beta = c.hbar * omegaQ_max * 1e9 / (T * 1e-3 * c.k)  # convert mK to K and use eV
        kappa = 1 / (omegaQ_max * 1e9 * T1 * 1e-6 * 2 * np.pi)
        bathParams = {'type': 'broadband', 'exp': exp, 'beta': beta, 'kappa': kappa, 'omegaC': 50., 'tol': 1e-6}
        bathParams_list = [bathParams for _ in range(len(omegaQ_list))]

        return {
            'omegaQ': omegaQ_list,
            'bath': bathParams_list,
            'strideTime': float(self.stride_time_entry.get()),
            'dtFB': float(self.dtFB_entry.get()),
            'gate_time': gate_time_list,
            'idlingTime': idling_time,
            'depth': [int(self.depth_entry.get())] * len(omegaQ_list),
            'bondDim': int(self.bondDim_entry.get()),
            'useRFPlus': self.useRFPlus_var.get(),
            'isRK13': self .RK13_var.get(),
        }

    def change_state(self, state):
        change_state_all_widgets(self, state=state)
        self.continue_button.configure(state=state)

# ----------------------------------------------------------------------
