import customtkinter as ctk

from .gui_utils import change_state_all_widgets

# ----------------------------------------------------------------------


class RightFrame(ctk.CTkFrame):
    def __init__(self, master):

        # initialization of the ctk.CTkFrame class
        super().__init__(master)
        row = 0

        # --------------------------------------------------------------

        # label
        self.logo_label = ctk.CTkLabel(
            self, text="Calculation", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
        row += 1

        # load result label and button
        self.load_result_label = ctk.CTkLabel(self, text="Load result (optional):")
        self.load_result_label.grid(row=row, column=0, padx=10, pady=10)
        self.load_result_button = ctk.CTkButton(
            self, text="Select file", command=master.load_result
        )
        self.load_result_button.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # back and submit button
        self.back_button = ctk.CTkButton(
            self, text="Back", command=master.back_to_middle_frame
        )
        self.back_button.grid(row=row, column=0, pady=10, padx=10)

        self.submit_button = ctk.CTkButton(self, text="Submit", command=master.submit)
        self.submit_button.grid(row=row, column=1, pady=10, padx=10)
        row += 1

        # empty row for spacing
        self.grid_rowconfigure(row, weight=1)
        row += 1

        # --------------------------------------------------------------

        # label
        self.logo_label = ctk.CTkLabel(
            self, text="Evaluation", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
        row += 1

        # calculate fidelity button
        self.calculate_fidelity_button = ctk.CTkButton(
            self, text="Calculate fidelity", command=master.calculate_fidelity
        )
        self.calculate_fidelity_button.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
        row += 1

        # calculate concurrence button
        self.calculate_concurrence_button = ctk.CTkButton(
            self, text="Calculate concurrence", command=master.calculate_concurrence
        )
        self.calculate_concurrence_button.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
        row += 1

        # empty row for spacing
        self.grid_rowconfigure(row, weight=1)
        row += 1

        # --------------------------------------------------------------

        # label
        self.logo_label2 = ctk.CTkLabel(
            self, text="Plotting", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label2.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
        row += 1

        # plot combobox
        self.plot_combobox = ctk.CTkComboBox(
            self, values=["Full density matrix", "other options"]
        )
        self.plot_combobox.set("Full density matrix")
        self.plot_combobox.grid(row=row, column=0, columnspan=2, padx=10, pady=10)
        row += 1

        # plot button
        self.plot_button = ctk.CTkButton(self, text="Plot", command=master.plot)
        self.plot_button.grid(row=row, column=0, columnspan=2, padx=10, pady=10)
        row += 1

        # --------------------------------------------------------------

    def get_kwargs(self):
        return {
            'plot_type': self.plot_combobox.get(),
        }

    def change_state1(self, state):
        self.load_result_button.configure(state=state)
        self.submit_button.configure(state=state)
        self.back_button.configure(state=state)
    
    def change_state2(self, state):
        self.calculate_fidelity_button.configure(state=state)
        self.calculate_concurrence_button.configure(state=state)
        self.plot_combobox.configure(state=state)
        self.plot_button.configure(state=state)


# ----------------------------------------------------------------------
