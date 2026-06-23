import customtkinter as ctk

from ...ssh import downloadResult
from ..gui_utils import make_section_label, PAD_OUTER, PAD_Y

# ----------------------------------------------------------------------


def _add_entry(parent, label_text, row, default="", show=None):
    """Helper: add a label + entry row, return the entry widget."""
    ctk.CTkLabel(
        parent, text=label_text, font=ctk.CTkFont(size=12), anchor="w"
    ).grid(row=row, column=0, padx=PAD_OUTER, pady=PAD_Y, sticky="w")
    kw = {"width": 240}
    if show is not None:
        kw["show"] = show
    entry = ctk.CTkEntry(parent, **kw)
    entry.insert(0, str(default))
    entry.grid(row=row, column=1, padx=PAD_OUTER, pady=PAD_Y, sticky="ew")
    return entry


# ----------------------------------------------------------------------


class HPCSettings(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("HPC Settings")
        self.geometry("480x680")
        self.resizable(False, False)
        self.master = master
        self.grid_columnconfigure(1, weight=1)

        row = 0
        row += make_section_label(self, "Login", row)

        self.hostname_entry = _add_entry(self, "Hostname:", row)
        row += 1
        self.username_entry = _add_entry(self, "Username:", row)
        row += 1
        self.password_entry = _add_entry(self, "Password:", row, show="●")
        row += 1
        self.otp_entry = _add_entry(self, "One-Time Password:", row, show="●")
        row += 1

        self.grid_rowconfigure(row, minsize=8)
        row += 1
        row += make_section_label(self, "Job Settings", row)

        self.scheduler_entry = _add_entry(self, "Scheduler:", row, default="slurm")
        row += 1
        self.nodes_entry = _add_entry(self, "Number of nodes:", row, default="1")
        row += 1
        self.cpus_entry = _add_entry(self, "CPUs per task:", row, default="4")
        row += 1
        self.time_entry = _add_entry(self, "Max time (D-H:MM:SS):", row, default="0-04:00:00")
        row += 1
        self.venv_entry = _add_entry(self, "Virtualenv path:", row, default="$HOME/.venv")
        row += 1
        self.email_entry = _add_entry(self, "Email (optional):", row)
        row += 1
        self.others_entry = _add_entry(self, "Extra #SBATCH directives:", row)
        row += 1

        self.grid_rowconfigure(row, weight=1)
        row += 1

        ctk.CTkButton(
            self, text="Confirm", width=160, command=self._confirm
        ).grid(row=row, column=0, columnspan=2, pady=PAD_OUTER)

    def _confirm(self):
        self.master.submissionParams = {
            "hostname":      self.hostname_entry.get(),
            "username":      self.username_entry.get(),
            "password":      self.password_entry.get(),
            "otp":           self.otp_entry.get(),
            "schedulerName": self.scheduler_entry.get(),
            "numNodes":      int(self.nodes_entry.get() or 1),
            "tasksPerNode":  1,
            "cpusPerTask":   int(self.cpus_entry.get() or 1),
            "maxTime":       self.time_entry.get(),
            "others":        self.others_entry.get(),
            "venvPath":      self.venv_entry.get(),
            "emailAddress":  self.email_entry.get(),
        }
        self.destroy()


# ----------------------------------------------------------------------


class HPCDownload(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("HPC Download")
        self.geometry("480x400")
        self.resizable(False, False)
        self.master = master
        self.grid_columnconfigure(1, weight=1)

        prev = master.submissionParams
        row = 0
        row += make_section_label(self, "Login", row)

        self.hostname_entry = _add_entry(
            self, "Hostname:", row, default=prev.get("hostname", "")
        )
        row += 1
        self.username_entry = _add_entry(
            self, "Username:", row, default=prev.get("username", "")
        )
        row += 1
        self.password_entry = _add_entry(self, "Password:", row, show="●")
        row += 1
        self.otp_entry = _add_entry(self, "One-Time Password:", row, show="●")
        row += 1

        self.grid_rowconfigure(row, minsize=8)
        row += 1
        row += make_section_label(self, "Job", row)

        self.job_id_entry = _add_entry(
            self, "Job ID:", row, default=master.job_id
        )
        row += 1
        self.scheduler_entry = _add_entry(
            self, "Scheduler:", row, default=prev.get("schedulerName", "slurm")
        )
        row += 1

        self.grid_rowconfigure(row, weight=1)
        row += 1

        ctk.CTkButton(
            self, text="Download", width=160, command=self._download
        ).grid(row=row, column=0, columnspan=2, pady=PAD_OUTER)

    def _download(self):
        download_params = {
            "hostname":      self.hostname_entry.get(),
            "username":      self.username_entry.get(),
            "password":      self.password_entry.get(),
            "otp":           self.otp_entry.get(),
            "schedulerName": self.scheduler_entry.get(),
        }
        self.master.job_id = self.job_id_entry.get()
        downloadResult(download_params, self.master.job_id,
                       self.master.job_id + ".csv")
        self.destroy()

# ----------------------------------------------------------------------
