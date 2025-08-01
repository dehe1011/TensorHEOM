import webbrowser
import time
import customtkinter as ctk
import numpy as np
from scipy.linalg import eigvals

from ..main import get_result

from .left_frame import LeftFrame
from .middle_frame import MiddleFrame
from .right_frame import RightFrame
from .help_frame import HelpFrame
from .scrollable_console_frame import ScrollableConsoleFrame
from .plotting_window import PlottingWindow

# --------------------------------------------------

class TensorHeomApp(ctk.CTk):
    def __init__(self):
        """ This window is the main window. """

        # initialization of the ctk.CTk class
        super().__init__()

        self.title("TensorHEOM")
        self.kwargs = {}
        self.target = np.array([
                [0.5, 0, 0, 0.5],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0.5, 0, 0, 0.5]
            ], dtype=complex)

        # Configure the grid layout for the root window
        self.grid_columnconfigure(0, weight=1)  # Column 0 takes 1 part
        self.grid_columnconfigure(1, weight=2)  # Column 1 takes 2 parts
        self.grid_columnconfigure(2, weight=1)  # Column 2 takes 1 part

        self.grid_rowconfigure(0, weight=5)  # Row 0 takes 2 parts
        self.grid_rowconfigure(1, weight=1)  # Row 1 takes 1 part

        # --------------------------------------------------------------

        # left frames
        self.left_frame = LeftFrame(self)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.help_frame = HelpFrame(self)
        self.help_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # --------------------------------------------------------------

        # middle frames
        self.middle_frame = MiddleFrame(self)
        self.middle_frame.grid(
            row=0, column=1, rowspan=3, padx=10, pady=10, sticky="nsew"
        )

        # --------------------------------------------------------------

        # right frames

        self.right_frame = RightFrame(self)
        self.right_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        self.scrollable_console_frame = ScrollableConsoleFrame(self)
        self.scrollable_console_frame.grid(
            row=1, column=2, padx=10, pady=10, rowspan=2, sticky="nsew"
        )

        # --------------------------------------------------------------

        # self.right_frame.change_state("disabled")

    # ------------------------------------------------------------------

    def open_github(self):
        webbrowser.open("https://github.com/dehe1011")

    def open_paper(self):
        webbrowser.open("https://journals.aps.org/prresearch/abstract/10.1103/PhysRevResearch.6.033215")

    def calculate(self): 
        t0 = time.time()
        print("Calculating...")
        self.right_frame.change_state("normal")
        self.middle_frame.change_state("disabled")
        self.left_frame.change_state("disabled")

        self.kwargs = {
            **self.left_frame.get_kwargs(),
            **self.middle_frame.get_kwargs()
        }
        self.result = get_result(**self.kwargs)

        dms = np.array(self.result.values)[:,1:]
        self.dms = np.array([dm.reshape(4, 4) for dm in dms])

        t1 = time.time()
        print(f"Calculation done in {t1-t0}s.")

    def back(self):
        self.right_frame.change_state("disabled")
        self.middle_frame.change_state("normal")
        self.left_frame.change_state("normal")

    def submit(self):
        self.plot_kwargs = self.right_frame.get_kwargs()
        self.plotting_window = PlottingWindow(self)

    def calculate_fidelity(self):
        # print("Calculating fidelity...")
        rho = self.dms[-1]
        F = np.real(np.trace(rho @ self.target))
        print(f"Fidelity: {F}")
        return F

    def calculate_concurrence(self):
        # print("Calculating concurrence...")
        rho = self.dms[-1]

        sigma_y = np.array([[0, -1j], [1j, 0]])
        Y = np.kron(sigma_y, sigma_y)
        rho_tilde = Y @ rho.conj() @ Y
        R = rho @ rho_tilde

        eigenvals = np.sort(np.sqrt(np.abs(eigvals(R))))[::-1]
        C = max(0, eigenvals[0] - sum(eigenvals[1:]))
        print(f"Concurrence: {C}")
        return C

# ----------------------------------------------------------------------
