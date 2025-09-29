import customtkinter as ctk

from .gui_utils import change_state_all_widgets, Counter
   
# ----------------------------------------------------------------------


class LeftFrame(ctk.CTkFrame):
    def __init__(self, master):

        # initialization of the ctk.CTkFrame class
        super().__init__(master)
        row = 0

        # --------------------------------------------------------------

        # label
        self.logo_label = ctk.CTkLabel(
            self, text="Circuit", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
        row += 1

        # num qubits label and entry
        self.num_qubits_label = ctk.CTkLabel(self, text="Number of qubits:")
        self.num_qubits_label.grid(row=row, column=0, padx=10, pady=10)
        row += 1

        # self.num_qubits_counter = Counter(self, start=1, minimum=1, maximum=3)
        self.num_qubits_counter = ctk.CTkComboBox(self, values=["1", "2", "3"])
        self.num_qubits_counter.set("1")
        self.num_qubits_counter.grid(row=row, column=0, padx=10, pady=10)
        row += 1

        # --------------------------------------------------------------

        # define circuit label
        self.define_circuit_label = ctk.CTkLabel(self, text="Define Circuit:")
        self.define_circuit_label.grid(row=row, column=0, pady=10, padx=10)
        row += 1

        # big circuit editor button
        self.circuit_editor_button = ctk.CTkButton(
            self, text="Open Circuit Editor", command=master.open_circuit_editor
        )
        self.circuit_editor_button.grid(row=row, column=0, columnspan=2, padx=10, pady=20)
        row += 1

        # big circuit upload button
        self.circuit_upload_button = ctk.CTkButton(
            self, text="Upload Circuit", command=master.load_circuit
        )
        self.circuit_upload_button.grid(row=row, column=0, columnspan=2, padx=10, pady=10)
        row += 1

        # --------------------------------------------------------------

        # empty row for spacing
        self.grid_rowconfigure(row, weight=1)
        row += 1

        # continue button
        self.continue_button = ctk.CTkButton(
            self, text="Continue", command=master.continue_to_middle_frame
        )
        self.continue_button.grid(row=row, column=0, padx=10, pady=20)
        row += 1

        # --------------------------------------------------------------

    def get_kwargs(self):
        return {'numQ': int(self.num_qubits_counter.get()) }

    def change_state(self, state):
        change_state_all_widgets(self, state=state)

# ----------------------------------------------------------------------
