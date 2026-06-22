import customtkinter as ctk
import numpy as np
import ast

from ..gui_utils import change_state_all_widgets

# ----------------------------------------------------------------------

class MiddleFrame(ctk.CTkFrame):
    def __init__(self, master):

        # initialization of the ctk.CTkFrame class
        super().__init__(master)
        self.master = master
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
        self.qubit_frequency_entry.insert(0, str([5] * self.master.numQ) ) # omegaQ_max = 5 * 2* np.pi
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
        self.oneq_gate_time_label = ctk.CTkLabel(self, text="1Q gate time (ns):")
        self.oneq_gate_time_label.grid(row=row, column=0, padx=10, pady=10)
        self.oneq_gate_time_entry = ctk.CTkEntry(self)
        self.oneq_gate_time_entry.insert(0, str([16] * self.master.numQ)) # omegaQ_max * 16
        self.oneq_gate_time_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # Gate time label and entry
        self.twoq_gate_time_label = ctk.CTkLabel(self, text="2Q gate time (ns):")
        self.twoq_gate_time_label.grid(row=row, column=0, padx=10, pady=10)
        self.twoq_gate_time_entry = ctk.CTkEntry(self)
        self.twoq_gate_time_entry.insert(0, str([50] * (self.master.numQ-1) )) # omegaQ_max * 16
        self.twoq_gate_time_entry.grid(row=row, column=1, padx=10, pady=10)
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
        
        # cutoff frequency label and entry
        self.omegaC_label = ctk.CTkLabel(self, text="Cutoff frequency (GHz):")
        self.omegaC_label.grid(row=row, column=0, padx=10, pady=10)
        self.omegaC_entry = ctk.CTkEntry(self)
        self.omegaC_entry.insert(0, 20) # omegaC = 20 * 2 * np.pi / omegaQ_max
        self.omegaC_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # AAA tolerance label and entry
        self.tol_label = ctk.CTkLabel(self, text="AAA tolerance:")
        self.tol_label.grid(row=row, column=0, padx=10, pady=10)
        self.tol_entry = ctk.CTkEntry(self)
        self.tol_entry.insert(0, 1e-4)
        self.tol_entry.grid(row=row, column=1, padx=10, pady=10)
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
        self.dtFB_label = ctk.CTkLabel(self, text="Simulation step (ps):")
        self.dtFB_label.grid(row=row, column=0, padx=10, pady=10)
        self.dtFB_entry = ctk.CTkEntry(self)
        self.dtFB_entry.insert(0, 1) # 1
        self.dtFB_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # depth label and integer entry
        self.depth_label = ctk.CTkLabel(self, text="Hierarchy depth:")
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
        self.useRFPlus_checkbox.grid(row=row, column=0, columnspan=1, padx=10, pady=10)

        # RK13 checkbox
        self.RK13_var = ctk.BooleanVar(value=False)
        self.RK13_checkbox = ctk.CTkCheckBox(self, text="Use RK13", variable=self.RK13_var)
        self.RK13_checkbox.grid(row=row, column=1, columnspan=1, padx=10, pady=10)
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

    def get_args(self):
            freqQ = ast.literal_eval(self.qubit_frequency_entry.get())
            gateTimeOneQ = ast.literal_eval(self.oneq_gate_time_entry.get())
            gateTimeTwoQ = ast.literal_eval(self.twoq_gate_time_entry.get())
            gateTime = gateTimeOneQ + gateTimeTwoQ
            T = float(self.temperature_entry.get())
            T1 = float(self.T1_time_entry.get())
            omegaC = float(self.omegaC_entry.get()) * 2 * np.pi
            exp = float(self.exponent_entry.get())
            tol = float(self.tol_entry.get())
            idlingTime = float(self.idling_time_entry.get())
            depth = [int(self.depth_entry.get())] * self.master.numQ
            dtFB = float(self.dtFB_entry.get())
            bondDim = int(self.bondDim_entry.get())
            useRFPlus = self.useRFPlus_var.get()
            isRK13 = self .RK13_var.get()
            return freqQ, gateTime, T, T1, omegaC, exp, tol, idlingTime, dtFB, depth, bondDim, useRFPlus, isRK13

    def change_state(self, state):
        change_state_all_widgets(self, state=state)
        self.continue_button.configure(state=state)

# ----------------------------------------------------------------------
