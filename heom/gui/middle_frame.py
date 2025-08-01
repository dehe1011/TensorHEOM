import customtkinter as ctk
import numpy as np

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
            self, text="Bath", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
        row += 1

        # exponent combobox
        self.exponent_label = ctk.CTkLabel(self, text="Exponent:")
        self.exponent_label.grid(row=row, column=0, padx=10, pady=10)
        self.exponent_combobox = ctk.CTkComboBox(
            self, values=["1", "1/2", "1/8"]
        )
        self.exponent_combobox.set("1")
        self.exponent_combobox.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # cutoff frequency label and entry
        self.cutoff_frequency_label = ctk.CTkLabel(self, text="Cutoff frequency (GHz):")
        self.cutoff_frequency_label.grid(row=row, column=0, padx=10, pady=10)
        self.cutoff_frequency_entry = ctk.CTkEntry(self)
        self.cutoff_frequency_entry.insert(0, 50)
        self.cutoff_frequency_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # temperature label and entry
        self.temperature_label = ctk.CTkLabel(self, text="Temperature (K):")
        self.temperature_label.grid(row=row + 1, column=0, padx=10, pady=10)
        self.temperature_entry = ctk.CTkEntry(self) 
        self.temperature_entry.insert(0, 5)
        self.temperature_entry.grid(row=row + 1, column=1, padx=10, pady=10)
        row += 1

        # system-bath coupling label and entry
        self.system_bath_coupling_label = ctk.CTkLabel(self, text="System-bath coupling (GHz):")
        self.system_bath_coupling_label.grid(row=row, column=0, padx=10, pady=10)
        self.system_bath_coupling_entry = ctk.CTkEntry(self)
        self.system_bath_coupling_entry.insert(0, 0.004)
        self.system_bath_coupling_entry.grid(row=row , column=1, padx=10, pady=10)
        row += 1

        # --------------------------------------------------------------

        # label
        self.logo_label2 = ctk.CTkLabel(
            self, text="Simulation", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label2.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
        row += 1

        # timestep label and entry
        self.timestep_label = ctk.CTkLabel(self, text="Timestep:")
        self.timestep_label.grid(row=row, column=0, padx=10, pady=10)
        self.timestep_entry = ctk.CTkEntry(self)
        self.timestep_entry.insert(0, 0.001)
        self.timestep_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # initial state label and entry
        self.initial_state_label = ctk.CTkLabel(self, text="Initial state:")
        self.initial_state_label.grid(row=row, column=0, padx=10, pady=10)
        self.initial_state_entry = ctk.CTkEntry(self)
        self.initial_state_entry.insert(0, "00")
        self.initial_state_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # --------------------------------------------------------------

        # label
        self.logo_label = ctk.CTkLabel(
            self, text="Drive", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
        row += 1

        # Rabi frequency label and entry
        self.rabi_frequency_label = ctk.CTkLabel(self, text="Rabi frequency (GHz):")
        self.rabi_frequency_label.grid(row=row, column=0, padx=10, pady=10)
        self.rabi_frequency_entry = ctk.CTkEntry(self)
        self.rabi_frequency_entry.insert(0, round(10*np.pi, 1) )
        self.rabi_frequency_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # drive frequency label and entry
        self.drive_frequency_label = ctk.CTkLabel(self, text="Drive frequency (GHz):")
        self.drive_frequency_label.grid(row=row, column=0, padx=10, pady=10)
        self.drive_frequency_entry = ctk.CTkEntry(self)
        self.drive_frequency_entry.insert(0, 1)
        self.drive_frequency_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # qubit coupling label and entry
        self.qubit_coupling_label = ctk.CTkLabel(self, text="Qubit coupling (GHz):")
        self.qubit_coupling_label.grid(row=row, column=0, padx=10, pady=10)
        self.qubit_coupling_entry = ctk.CTkEntry(self)
        self.qubit_coupling_entry.insert(0, round(10*np.pi, 1) )
        self.qubit_coupling_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # --------------------------------------------------------------

        # confirm button
        self.calculate_button = ctk.CTkButton(
            self, text="Calculate", command=master.calculate
        )
        self.calculate_button.grid(row=row, column=0, columnspan=2, pady=10, padx=10)


    def get_kwargs(self):
        init_state_entry = self.initial_state_entry.get()
        if init_state_entry == "00":
            init_state = np.array(
                [[1, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]], dtype=np.complex128)
        if init_state_entry == "01":
            init_state = np.array(
                [[0, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]], dtype=np.complex128)
        if init_state_entry == "10":
            init_state = np.array(
                [[0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 0]], dtype=np.complex128)
        if init_state_entry == "11":
            init_state = np.array(
                [[0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 1]], dtype=np.complex128)
        return {
            's': float(self.exponent_combobox.get()),
            'omega_c': float(self.cutoff_frequency_entry.get()),
            'T': float(self.temperature_entry.get()),
            'kappa': float(self.system_bath_coupling_entry.get()),
            'dtFB': float(self.timestep_entry.get()),
            'init_state': init_state,
        }

    def change_state(self, state):
        change_state_all_widgets(self, state=state)
        self.calculate_button.configure(state=state)

# ----------------------------------------------------------------------
