import customtkinter as ctk

from ..gui_utils import change_state_all_widgets, Counter
   
# ----------------------------------------------------------------------


class LeftFrame(ctk.CTkFrame):
    def __init__(self, master):

        # initialization of the ctk.CTkFrame class
        super().__init__(master)
        self.master = master
        row = 0

        # qubit architecture combobox
        # self.qubit_architecture_label = ctk.CTkLabel(self, text="Qubit architecture:")
        # self.qubit_architecture_label.grid(row=row, column=0, padx=10, pady=10)
        # row += 1

        # self.qubit_architecture_combobox = ctk.CTkComboBox(
        #     self, values=["chain"]
        # )
        # self.qubit_architecture_combobox.set("chain")
        # self.qubit_architecture_combobox.grid(row=row, column=0, padx=10, pady=10)
        # row += 1

        # # empty row for spacing
        # self.grid_rowconfigure(row, weight=1)
        # row += 1

        # --------------------------------------------------------------

        # label
        self.logo_label = ctk.CTkLabel(
            self, text="Circuit", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
        row += 1

        # num qubits counter
        self.num_qubits_label = ctk.CTkLabel(self, text="Number of qubits:")
        self.num_qubits_label.grid(row=row, column=0, padx=10, pady=10)
        row += 1

        self.num_qubits_counter = Counter(self, start=self.master.numQ, minimum=1, maximum=9)
        self.num_qubits_counter.grid(row=row, column=0, padx=10, pady=10)
        row += 1

        # open circuit editor button
        self.circuit_editor_button = ctk.CTkButton(
            self, text="Open circuit editor", command=master.open_circuit_editor
        )
        self.circuit_editor_button.grid(row=row, column=0, columnspan=2, padx=10, pady=20)
        row += 1

        # upload circuit button
        self.circuit_upload_button = ctk.CTkButton(
            self, text="Upload circuit", command=master.upload_circuit
        )
        self.circuit_upload_button.grid(row=row, column=0, columnspan=2, padx=10, pady=10)
        row += 1

        # empty row for spacing
        self.grid_rowconfigure(row, weight=1)
        row += 1

        # --------------------------------------------------------------

        # label
        self.logo_label = ctk.CTkLabel(
            self, text="Saving", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
        row += 1

        # directory label and entry
        self.directory_label = ctk.CTkLabel(self, text="Directory:")
        self.directory_label.grid(row=row, column=0, padx=10, pady=10)
        row += 1
        self.directory_entry = ctk.CTkEntry(self)
        self.directory_entry.insert(0, self.master.directory)
        self.directory_entry.grid(row=row, column=0, padx=10, pady=10)
        row += 1

        # filename label and entry
        self.filename_label = ctk.CTkLabel(self, text="Filename:")
        self.filename_label.grid(row=row, column=0, padx=10, pady=10)
        self.filename_entry = ctk.CTkEntry(self)   
        row += 1
        self.filename_entry.insert(0, self.master.fileName)
        self.filename_entry.grid(row=row, column=0, padx=10, pady=10)
        row += 1

        # empty row for spacing
        self.grid_rowconfigure(row, weight=1)
        row += 1

        # --------------------------------------------------------------

        # continue button
        self.continue_button = ctk.CTkButton(
            self, text="Continue", command=master.continue_to_middle_frame
        )
        self.continue_button.grid(row=row, column=0, padx=10, pady=20)
        row += 1

        # --------------------------------------------------------------

    def get_args(self):
        directory = self.directory_entry.get()
        filename = self.filename_entry.get()
        numQ = int(self.num_qubits_counter.get())
        return directory, filename, numQ

    def change_state(self, state):
        change_state_all_widgets(self, state=state)

# ----------------------------------------------------------------------
