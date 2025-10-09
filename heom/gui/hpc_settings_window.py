import customtkinter as ctk

from ..ssh import downloadResult

# ----------------------------------------------------------------------

class HPCSettings(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("HPC Settings")
        self.geometry("400x750")
        self.master = master

        row = 0

        # Login label
        login_label = ctk.CTkLabel(self, text="Login", font=ctk.CTkFont(size=16, weight="bold"))
        login_label.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1

        self.hostname_entry = self.add_entry("Hostname:", row)
        self.hostname_entry.insert(0, "justus2.uni-ulm.de")
        self.username_entry = self.add_entry("Username:", row+1)
        self.username_entry.insert(0, "ul_kfo52")
        self.password_entry = self.add_entry("Password:", row+2)
        self.password_entry.insert(0, "3bA5huBB5n!NdU8")
        self.otp_entry = self.add_entry("One-Time Password:", row+3)
        row += 4

        # Submission label
        submission_label = ctk.CTkLabel(self, text="Job Settings", font=ctk.CTkFont(size=16, weight="bold"))
        submission_label.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        
        self.scheduler_entry = self.add_entry("Scheduler Name:", row)
        self.scheduler_entry.insert(0, "slurm")
        self.nodes_entry = self.add_entry("Number of Nodes:", row+1)
        self.nodes_entry.insert(0, "1")
        self.tasks_entry = self.add_entry("Tasks per Node:", row+2)
        self.tasks_entry.insert(0, "1")
        self.cpus_entry = self.add_entry("CPUs per Task:", row+3)
        self.cpus_entry.insert(0, "4")
        self.time_entry = self.add_entry("Max Time (D-HH:MM:SS):", row+4)
        self.time_entry.insert(0, "336:00:00")
        self.others_entry = self.add_entry("Other Parameters:", row+5)
        self.others_entry.insert(0, "")
        self.venv_entry = self.add_entry("Virtual Env Path:", row+6)
        self.venv_entry.insert(0, "$HOME/python_HEOM/.venv")
        self.email_entry = self.add_entry("Email (optional):", row+7)
        self.email_entry.insert(0, "dennis.herb@uni-ulm.de")
        row += 8

        # empty row for spacing
        self.grid_rowconfigure(row, weight=1)
        row += 1

        # Confirm button
        confirm_btn = ctk.CTkButton(self, text="Confirm", command=self.confirm)
        confirm_btn.grid(row=row, column=0, columnspan=2, pady=10)

    def add_entry(self, label_text, row):
        """Helper to add a label + entry field"""
        label = ctk.CTkLabel(self, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=10, sticky="w")
        entry = ctk.CTkEntry(self, width=220)
        entry.grid(row=row, column=1, padx=10, pady=10)
        return entry

    def confirm(self):
        """Collect all entries into submissionParams dict"""

        submissionParams1 = {
            "hostname": self.hostname_entry.get(),
            "username": self.username_entry.get(),
            "password": self.password_entry.get(),
            "otp": self.otp_entry.get(),
        }

        submissionParams2 = {
            "schedulerName": self.scheduler_entry.get(),
            "numNodes": int(self.nodes_entry.get()),
            "tasksPerNode": int(self.tasks_entry.get()),
            "cpusPerTask": int(self.cpus_entry.get()),
            "maxTime": self.time_entry.get(),
            "others": self.others_entry.get(),
            "venvPath": self.venv_entry.get(),
            "emailAddress": self.email_entry.get(),
        }
        self.master.submissionParams = {**submissionParams1, **submissionParams2}
        self.destroy()

# ----------------------------------------------------------------------

class HPCDownload(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("HPC Download")
        self.geometry("400x450")
        self.master = master

        row = 0

        # Login label
        login_label = ctk.CTkLabel(self, text="Login", font=ctk.CTkFont(size=16, weight="bold"))
        login_label.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1

        self.hostname_entry = self.add_entry("Hostname:", row)
        self.hostname_entry.insert(0, master.submissionParams.get("hostname", "justus2.uni-ulm.de"))

        self.username_entry = self.add_entry("Username:", row+1)
        self.username_entry.insert(0, master.submissionParams.get("username", "ul_kfo52"))

        self.password_entry = self.add_entry("Password:", row+2)
        self.password_entry.insert(0, master.submissionParams.get("password", "3bA5huBB5n!NdU8"))

        self.otp_entry = self.add_entry("One-Time Password:", row+3)
        self.otp_entry.insert(0, "")
        row += 4

        # Job info label
        job_label = ctk.CTkLabel(self, text="Job Settings", font=ctk.CTkFont(size=16, weight="bold"))
        job_label.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1

        self.job_id_entry = self.add_entry("Job ID:", row)
        self.job_id_entry.insert(row, master.job_id)
        
        self.scheduler_entry = self.add_entry("Scheduler Name:", row+1)
        self.scheduler_entry.insert(0, master.submissionParams.get("schedulerName", "slurm"))
        row += 2

        # empty row for spacing
        self.grid_rowconfigure(row, weight=1)
        row += 1

        # Confirm button
        confirm_btn = ctk.CTkButton(self, text="Confirm", command=self.download)
        confirm_btn.grid(row=row, column=0, columnspan=2, pady=10)

    def add_entry(self, label_text, row):
        """Helper to add a label + entry field"""
        label = ctk.CTkLabel(self, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=10, sticky="w")
        entry = ctk.CTkEntry(self, width=220)
        entry.grid(row=row, column=1, padx=10, pady=10)
        return entry

    def download(self):
        """Collect all entries into downloadParams dict"""

        downloadParams = {
            "hostname": self.hostname_entry.get(),
            "username": self.username_entry.get(),
            "password": self.password_entry.get(),
            "otp": self.otp_entry.get(),
            "schedulerName": self.scheduler_entry.get(),
        }
        self.master.job_id = self.job_id_entry.get()
        downloadResult(downloadParams, self.master.job_id, self.master.job_id + ".csv")
        # print(f"Downloaded result as {self.master.fileName}.")
        self.destroy()

# ----------------------------------------------------------------------
