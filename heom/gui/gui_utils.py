import customtkinter as ctk
import pandas as pd
import numpy as np

# ----------------------------------------------------------------------


def change_state_all_widgets(frame, state):
    for widget in frame.winfo_children():
        if isinstance(
            widget, ctk.CTkBaseClass
        ):  # Check if the widget is a customtkinter widget
            widget.configure(state=state)
        elif isinstance(
            widget, ctk.CTkFrame
        ):  # Recursively disable widgets in nested frames
            change_state_all_widgets(widget, state)

class Counter(ctk.CTkFrame):
    def __init__(self, master=None, start=1, minimum=1, maximum=3):
        super().__init__(master)
        self.value = start
        self.min_val = minimum
        self.max_val = maximum

        self.decrease_btn = ctk.CTkButton(self, text="-", width=40, command=self.decrease)
        self.decrease_btn.pack(side="left", padx=5)

        self.label = ctk.CTkLabel(self, text=str(self.value), width=40)
        self.label.pack(side="left", padx=5)

        self.increase_btn = ctk.CTkButton(self, text="+", width=40, command=self.increase)
        self.increase_btn.pack(side="left", padx=5)

    def increase(self):
        if self.value < self.max_val:
            self.value += 1
            self.label.configure(text=str(self.value))

    def decrease(self):
        if self.value > self.min_val:
            self.value -= 1
            self.label.configure(text=str(self.value))

    def get(self):
        return self.value

    def configure(self, state):
        """Enable/disable the counter"""
        self.increase_btn.configure(state=state)
        self.decrease_btn.configure(state=state)

# ----------------------------------------------------------------------

def load_density_matrices(csv_file):
    """
    Load timesteps and density matrices from CSV.

    Parameters
    ----------
    csv_file : str
        Path to the CSV file. The first column is time,
        then real and imaginary parts of the density matrix
        entries in row-major order.

    Returns
    -------
    times : np.ndarray
        1D array of time points.
    rhos : list of np.ndarray
        List of density matrices, one per row.
    """
    df = pd.read_csv(csv_file)
    times = df.iloc[:, 0].to_numpy()
    data = df.iloc[:, 1:].to_numpy()

    # Each complex number is two columns: (Re, Im)
    n_entries = data.shape[1] // 2
    dim = int(np.sqrt(n_entries))

    rhos = []
    for row in data:
        complex_entries = row[0::2] + 1j * row[1::2]
        rho = complex_entries.reshape((dim, dim))
        rhos.append(rho)

    return times, rhos

# ----------------------------------------------------------------------
