import customtkinter as ctk

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
        self.load_result_label = ctk.CTkLabel(self, text="1. Upload result:")
        self.load_result_label.grid(row=row, column=0, padx=10, pady=10)
        self.load_result_button = ctk.CTkButton(
            self, text="Upload file", command=master.upload_file
        )
        self.load_result_button.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # submit local button	
        self.submit_label = ctk.CTkLabel(self, text="2. Calculate locally:")
        self.submit_label.grid(row=row, column=0, padx=10, pady=10)
        self.submit_button = ctk.CTkButton(self, text="Submit", command=master.submit_local)
        self.submit_button.grid(row=row, column=1, pady=10, padx=10)
        row += 1

        # submit HPC button
        self.submit_HPC_label = ctk.CTkLabel(self, text="3. Submit to HPC:")
        self.submit_HPC_label.grid(row=row, column=0, padx=10, pady=10)
        self.submit_hpc_button = ctk.CTkButton(self, text="Submit", command=master.submit_hpc)
        self.submit_hpc_button.grid(row=row, column=1, pady=10, padx=10)
        row += 1

        # download label and button
        self.download_button = ctk.CTkButton(
            self, text="Download file", command=master.download_file
        )
        self.download_button.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # back button
        self.back_button = ctk.CTkButton(
            self, text="Back", command=master.back_to_middle_frame
        )
        self.back_button.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
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

        # plot pulse sequence button
        self.plot_pulse_seq_button = ctk.CTkButton(
            self, text="Plot pulse sequence", command=master.open_plotting_pulse_window)
        self.plot_pulse_seq_button.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
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
            self, values=["RDO", "Fidelity", "Concurrence"]
        )
        self.plot_combobox.set("RDO")
        self.plot_combobox.grid(row=row, column=0, columnspan=1, padx=10, pady=10)
        # row += 1

        # plot button
        self.plot_button = ctk.CTkButton(self, text="Plot", command=master.plot)
        self.plot_button.grid(row=row, column=1, columnspan=1, padx=10, pady=10)
        row += 1

        # --------------------------------------------------------------

    def get_args(self):
        plot_type = self.plot_combobox.get()
        return plot_type

    def change_state1(self, state):
        self.load_result_button.configure(state=state)
        self.download_button.configure(state=state)
        self.submit_button.configure(state=state)
        self.submit_hpc_button.configure(state=state)
        self.back_button.configure(state=state)
        self.plot_pulse_seq_button.configure(state=state)
    
    def change_state2(self, state):
        self.calculate_fidelity_button.configure(state=state)
        self.calculate_concurrence_button.configure(state=state)
        self.plot_combobox.configure(state=state)
        self.plot_button.configure(state=state)

# ----------------------------------------------------------------------
