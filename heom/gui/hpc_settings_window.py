import customtkinter as ctk

# ----------------------------------------------------------------------

class HPCSettings(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("HPC Settings")
        self.geometry("400x400")
        self.master = master

        # --- Widgets for input fields ---
        self.scheduler_entry = self.add_entry("Scheduler Name:", 0)
        self.nodes_entry = self.add_entry("Number of Nodes:", 1)
        self.tasks_entry = self.add_entry("Tasks per Node:", 2)
        self.cpus_entry = self.add_entry("CPUs per Task:", 3)
        self.time_entry = self.add_entry("Max Time (D-HH:MM:SS):", 4)
        self.others_entry = self.add_entry("Other Parameters:", 5)
        self.venv_entry = self.add_entry("Virtual Env Path:", 6)

        # Confirm button
        confirm_btn = ctk.CTkButton(self, text="Confirm", command=self.confirm)
        confirm_btn.grid(row=7, column=0, columnspan=2, pady=10)

    def add_entry(self, label_text, row):
        """Helper to add a label + entry field"""
        label = ctk.CTkLabel(self, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=10, sticky="w")
        entry = ctk.CTkEntry(self, width=220)
        entry.grid(row=row, column=1, padx=10, pady=10)
        return entry

    def confirm(self):
        """Collect all entries into submissionParams dict"""

        self.master.submissionParams = {
            "schedulerName": self.scheduler_entry.get(),
            "numNodes": int(self.nodes_entry.get()),
            "tasksPerNode": int(self.tasks_entry.get()),
            "cpusPerTask": int(self.cpus_entry.get()),
            "maxTime": self.time_entry.get(),
            "others": self.others_entry.get(),
            "venvPath": self.venv_entry.get(),
        }
        print("HPC settings:", self.master.submissionParams)

# ----------------------------------------------------------------------
