import os
import webbrowser
import time
import inspect

import customtkinter as ctk
from tkinter import filedialog
import qutip as q
from qiskit.quantum_info import Operator
from qiskit import QuantumCircuit

from ..main import prepareTTs, prepareArgs, calcTimeEvo
from ..evaluation import getFidelity, getConcurrence, loadResult, plotPulseSeq
from ..ssh import submitJob, loadQC

from .frames.left_frame import LeftFrame
from .frames.middle_frame import MiddleFrame
from .frames.right_frame import RightFrame
from .frames.help_frame import HelpFrame
from .frames.scrollable_console_frame import ScrollableConsoleFrame

from .windows.circuit_editor_window import CircuitEditor
from .windows.help_window import HelpWindow
from .windows.state_editor_window import StateEditor
from .windows.plotting_pulse_window import PlottingPulseWindow
 
from .windows.hpc_settings_window import HPCSettings, HPCDownload
from .windows.plotting_window import PlottingWindow

from .gui_utils import StepIndicator

# ----------------------------------------------------------------------

def filter_kwargs(func, kwargs):
    sig = inspect.signature(func)
    return {k: v for k, v in kwargs.items() if k in sig.parameters}

# ----------------------------------------------------------------------

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# ----------------------------------------------------------------------

class TensorHeomApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TensorHEOM")
        self.minsize(900, 600)

        # ── state ────────────────────────────────────────────────────────
        self.numQ = 2
        self.directory_display = "simulations_GUI"
        self.directory = None
        self.fileName = "package_test" 
        self.kwargs = {}

        self.qc = None
        self.metadata = {}
        self.qcFilePath = None
        self.csvFilePath = None
        self.params = {}

        self.submissionParams, self.job_id = {}, ""
        self.t_list = None
        self.dm_list = None
        self.plot_kwargs = {}

        # ── root grid ────────────────────────────────────────────────────
        self.grid_columnconfigure(0, weight=0, minsize=220)  # left
        self.grid_columnconfigure(1, weight=1, minsize=400)  # middle
        self.grid_columnconfigure(2, weight=0, minsize=240)  # right
        self.grid_rowconfigure(0, weight=0)  # header
        self.grid_rowconfigure(1, weight=5)  # main content
        self.grid_rowconfigure(2, weight=1)  # console

        # ── header ───────────────────────────────────────────────────────
        self._header = ctk.CTkFrame(self, height=52, corner_radius=0,
                                    fg_color=("gray90", "gray15"))
        self._header.grid(row=0, column=0, columnspan=3, sticky="ew")
        self._header.grid_propagate(False)
        self._header.grid_columnconfigure(1, weight=1)

        self._title_lbl = ctk.CTkLabel(
            self._header, text="  TensorHEOM",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=("#1a73e8", "#4fa3f7"),
        )
        self._title_lbl.grid(row=0, column=0, padx=(16, 0), pady=8, sticky="w")

        self._step_indicator = StepIndicator(self._header)
        self._step_indicator.grid(row=0, column=1, pady=8)

        self._appearance_menu = ctk.CTkOptionMenu(
            self._header,
            values=["System", "Light", "Dark"],
            width=110,
            command=lambda m: ctk.set_appearance_mode(m),
        )
        self._appearance_menu.set("System")
        self._appearance_menu.grid(row=0, column=2, padx=16, pady=8, sticky="e")

        # ── left column ──────────────────────────────────────────────────
        self.left_frame = LeftFrame(self)
        self.left_frame.grid(row=1, column=0, padx=(10, 5), pady=(10, 5),
                             sticky="nsew")

        self.help_frame = HelpFrame(self)
        self.help_frame.grid(row=2, column=0, padx=(10, 5), pady=(5, 10),
                             sticky="nsew")

        # ── middle column ────────────────────────────────────────────────
        self.middle_frame = MiddleFrame(self)
        self.middle_frame.grid(row=1, column=1, rowspan=2, padx=5, pady=10,
                               sticky="nsew")

        # ── right column ─────────────────────────────────────────────────
        self.right_frame = RightFrame(self)
        self.right_frame.grid(row=1, column=2, padx=(5, 10), pady=(10, 5),
                              sticky="nsew")

        self.console_frame = ScrollableConsoleFrame(self)
        self.console_frame.grid(row=2, column=2, padx=(5, 10), pady=(5, 10),
                                sticky="nsew")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _set_step(self, step: int):
        self._step_indicator.set_step(step)

    # ------------------------------------------------------------------
    # Help frame functions
    # ------------------------------------------------------------------

    def open_github(self):
        webbrowser.open("https://github.com/dehe1011/TensorHEOM")

    def open_paper(self):
        webbrowser.open("http://arxiv.org/abs/2510.05872")

    def open_help_window(self):
        print("Opening help window...")
        popup = HelpWindow(self)
        popup.grab_set()
        self.wait_window(popup)

    # ------------------------------------------------------------------
    # Left frame functions
    # ------------------------------------------------------------------

    def open_circuit_editor(self):
        self.directory_display, self.fileName, self.numQ = self.left_frame.get_args()
        self.directory = os.path.join(os.getcwd(), self.directory_display)
        os.makedirs(self.directory, exist_ok=True)
        self.qcFilePath = os.path.join(self.directory, "qcData_" + self.fileName)

        print("Opening circuit editor window...")
        popup = CircuitEditor(self)
        popup.grab_set()
        self.wait_window(popup)

        if popup._circuit_built:
            print(f"Circuit built and saved as {self.qcFilePath}")
        else:
            print("No circuit was built or saved.")


    def upload_circuit(self):
        self.directory_display, self.fileName, self.numQ = self.left_frame.get_args()
        self.directory = os.path.join(os.getcwd(), self.directory_display)
        os.makedirs(self.directory, exist_ok=True)
        self.qcFilePath = os.path.join(self.directory, "qcData_" + self.fileName)

        print("Uploading circuit...")
        path = filedialog.askopenfilename(
            initialdir=self.directory,
            filetypes=[("QPY files", "*.qpy")],
        )

        if not path:
            print("No circuit file selected.")
        else: 
            self.qcFilePath = path
            self.qc = loadQC(self.qcFilePath)
            self.metadata = self.qc.metadata
            print(f"Found metadata in the uploaded circuit: {self.metadata}")
            print(f"Circuit uploaded successfully from {path}.")


    def continue_to_middle_frame(self):
        if self.qc is None:
            print("Please create or upload a quantum circuit before continuing.")
            return

        self.directory_display, self.fileName, self.numQ = self.left_frame.get_args()
        self.directory = os.path.join(os.getcwd(), self.directory_display)
        os.makedirs(self.directory, exist_ok=True)
        print(f"Directory set to: {self.directory}")

        self.qcFilePath = os.path.join(self.directory, "qcData_" + self.fileName + '.qpy')
        self.csvFilePath = os.path.join(self.directory, self.fileName + ".csv")

        if self.qc.num_qubits != self.numQ:
            print(
                f"Warning: circuit has {self.qc.num_qubits} qubit(s) but "
                f"{self.numQ} were specified. Using {self.qc.num_qubits}."
            )
            self.numQ = self.qc.num_qubits

        self.kwargs["directory"] = self.directory
        self.kwargs["fileName"] = self.fileName
        self.kwargs["numQ"] = self.numQ
        self.kwargs["rhoIni"] = (
            q.tensor([q.fock_dm(2, 0) for _ in range(self.numQ)]).full().real
        )

        self.left_frame = LeftFrame(self)
        self.left_frame.grid(row=1, column=0, padx=(10, 5), pady=(10, 5),
                             sticky="nsew")
        self.left_frame.change_state("disabled")

        self.middle_frame = MiddleFrame(self)
        self.middle_frame.grid(row=1, column=1, rowspan=2, padx=5, pady=10,
                               sticky="nsew")
        self._set_step(1)

    # ------------------------------------------------------------------
    # Middle frame functions
    # ------------------------------------------------------------------

    def open_state_editor(self):
        print("Opening state editor window...")

        popup = StateEditor(self)
        popup.grab_set()
        self.wait_window(popup)

        if getattr(popup, "state_confirmed", False):
            print("Initial state confirmed. Using:")
            print(self.kwargs["rhoIni"])
        else:
            print("Initial state was not confirmed.")
            print("Using the current/default initial state instead:")
            print(self.kwargs["rhoIni"])

    def back_to_left_frame(self):
        self.right_frame.change_state1("disabled")
        self.right_frame.change_state2("disabled")
        self.middle_frame.change_state("disabled")
        self.left_frame.change_state("normal")
        self._set_step(0)

    def continue_to_right_frame(self):
        (
            freqQ, gateTime, T, T1, omegaC, exp, tol,
            idlingTime, dtFB, depth, bondDim, strideTime, useRFPlus, isRK13,
        ) = self.middle_frame.get_args()

        self.kwargs.update(
            freqQ=freqQ, gateTime=gateTime, T=T, T1=T1,
            omegaC=omegaC, exp=exp, tol=tol, idlingTime=idlingTime,
            dtFB=dtFB, depth=depth, bondDim=bondDim, strideTime=strideTime,
            useRFPlus=useRFPlus, isRK13=isRK13, qc=self.qc,
        )

        print("Using the following parameters for simulation:")
        print(self.kwargs)
        
        self.middle_frame.change_state("disabled")
        self.right_frame.change_state1("normal")
        self._set_step(2)

    def open_plotting_pulse_window(self):
        print("Opening pulse sequence plotting window...")
        PlottingPulseWindow(self)
        # PlottingCircWindow(self)

    def plot_pulse_seq(self):
        return plotPulseSeq(**self.kwargs)

    # ------------------------------------------------------------------
    # Right frame functions
    # ------------------------------------------------------------------

    def upload_file(self):
        print("Uploading result file...")
        filepath = filedialog.askopenfilename(
            initialdir=self.directory,
            filetypes=[("CSV files", "*.csv")],
        )            
        if not filepath:
            print("No result file selected.")
            return
        self.t_list, self.dm_list = loadResult(filepath)
        self.t_list /= self.params.get("omegaQmax", 1.0)
        print("Result file uploaded successfully.")
        self.right_frame.change_state2("normal")
        self._set_step(3)

    def submit_local(self):
        print("Running simulation locally…")
        t0 = time.time()
        calcTimeEvo(**self.kwargs)
        self.t_list, self.dm_list = loadResult(self.csvFilePath)
        self.t_list /= self.params.get("omegaQmax", 1.0)
        elapsed = time.time() - t0
        print(f"Simulation finished in {elapsed:.1f} s. Saved to {self.csvFilePath}.")
        self.right_frame.change_state2("normal")
        self._set_step(3)

    def submit_hpc(self):
        print("Opening HPC Submission window...")
        popup = HPCSettings(self)
        popup.grab_set()
        self.wait_window(popup)

        if not self.submissionParams:
            print("HPC submission cancelled.")
            return

        print("Submitting job to HPC...")
        stride = int(self.kwargs["strideTime"] / self.kwargs["dtFB"])
        args = prepareArgs(
            self.kwargs["numQ"], self.kwargs["freqQ"], self.kwargs["gateTime"],
            self.kwargs["T"], self.kwargs["T1"], self.kwargs["omegaC"],
            self.kwargs["exp"], self.kwargs["tol"], self.kwargs["rhoIni"],
            self.kwargs["idlingTime"], self.kwargs["dtFB"],
            self.kwargs["depth"], self.kwargs["bondDim"],
        )
        omegaQmax, rho, bondDim, V, depth, bath, gateList, dtFB, idlingTime = args
        self.job_id = submitJob(
            self.submissionParams, self.qcFilePath, omegaQmax,
            self.kwargs["qc"], idlingTime, gateList, rho, bath, V,
            dtFB, stride, depth, bondDim,
            useRFPlus=self.kwargs["useRFPlus"],
            isRK13=self.kwargs["isRK13"],
        )

    def download_file(self):
        print("Opening HPC Download window...")
        popup = HPCDownload(self)
        popup.grab_set()
        self.wait_window(popup)

        if not getattr(popup, "download_successful", False):
            print("No result was downloaded.")
            return

        self.t_list, self.dm_list = loadResult(self.csvFilePath)
        self.t_list /= self.params.get("omegaQmax", 1.0)

        print(f"Result downloaded and saved as {self.csvFilePath}.")
        self.right_frame.change_state2("normal")
        self._set_step(3)

    def back_to_middle_frame(self):
        self.t_list = None
        self.dm_list = None
        self.right_frame.change_state1("disabled")
        self.right_frame.change_state2("disabled")
        self.middle_frame.change_state("normal")
        self.left_frame.change_state("disabled")
        self._set_step(1)

    # ------------------------------------------------------------------
    # Plotting / evaluation functions
    # ------------------------------------------------------------------

    def calculate_fidelity(self):
        rho = self.dm_list[-1]
        U = Operator(self.qc).data
        target = U @ self.kwargs["rhoIni"] @ U.conj().T
        F = getFidelity(rho, target)
        print(f"Fidelity: {F:.6f}")
        return F

    def calculate_concurrence(self):
        if self.numQ != 2:
            print("Concurrence is only defined for 2 qubits.")
            return None
        rho = self.dm_list[-1]
        C = getConcurrence(rho)
        print(f"Concurrence: {C:.6f}")
        return C

    def plot(self):
        plot_type = self.right_frame.get_args()
        self.plot_kwargs["plot_type"] = plot_type
        PlottingWindow(self)

# ----------------------------------------------------------------------
