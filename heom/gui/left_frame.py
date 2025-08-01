import customtkinter as ctk

from .gui_utils import change_state_all_widgets

# ----------------------------------------------------------------------


class LeftFrame(ctk.CTkFrame):
    def __init__(self, master):

        # initialization of the ctk.CTkFrame class
        super().__init__(master)
        row = 0

        # --------------------------------------------------------------

        # label
        self.logo_label = ctk.CTkLabel(
            self, text="System", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=row, column=0, pady=10, padx=10)
        row += 1

        #num qubits label and entry
        self.num_qubits_label = ctk.CTkLabel(self, text="Number of qubits:")
        self.num_qubits_label.grid(row=row, column=0, padx=10, pady=10)
        row += 1

        self.num_qubits_entry = ctk.CTkEntry(self)
        self.num_qubits_entry.insert(0, 2)
        self.num_qubits_entry.grid(row=row, column=0, padx=10, pady=10)
        row += 1

        # qubit architecture combobox
        self.qubit_architecture_label = ctk.CTkLabel(self, text="Qubit architecture:")
        self.qubit_architecture_label.grid(row=row, column=0, padx=10, pady=10)
        row += 1

        self.qubit_architecture_combobox = ctk.CTkComboBox(
            self, values=["single chain", "double chain"]
        )
        self.qubit_architecture_combobox.set("single chain")
        self.qubit_architecture_combobox.grid(row=row, column=0, padx=10, pady=10)
        row += 1

        # qubit frequency label and entry
        self.qubit_frequency_label = ctk.CTkLabel(self, text="Qubit frequency (GHz):")
        self.qubit_frequency_label.grid(row=row, column=0, padx=10, pady=10)
        row += 1

        self.qubit_frequency_entry = ctk.CTkEntry(self)
        self.qubit_frequency_entry.insert(0, 5)
        self.qubit_frequency_entry.grid(row=row, column=0, padx=10, pady=10)

    def get_kwargs(self):
        return {
            'numQ': int(self.num_qubits_entry.get()),
            'architecture': self.qubit_architecture_combobox.get(),
            'omegaQ': float(self.qubit_frequency_entry.get()),
        }

    def change_state(self, state):
        change_state_all_widgets(self, state=state)

# ----------------------------------------------------------------------
