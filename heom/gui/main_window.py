import webbrowser
import time
import inspect

import customtkinter as ctk
from tkinter import filedialog
import numpy as np
import qutip as q
from qiskit.quantum_info import Operator
from qiskit import qpy

from ..main import main
from ..evaluation import getFidelity, getConcurrence, loadResult
from ..ssh import submitJob

from .frames.left_frame import LeftFrame
from .frames.middle_frame import MiddleFrame
from .frames.right_frame import RightFrame
from .frames.help_frame import HelpFrame
from .frames.scrollable_console_frame import ScrollableConsoleFrame

from .windows.circuit_editor_window import CircuitEditor
from .windows.help_window import HelpWindow
from .windows.state_editor_window import StateEditor
from .windows.hpc_settings_window import HPCSettings, HPCDownload
from .windows.plotting_window import PlottingWindow

# ----------------------------------------------------------------------

def filter_kwargs(func, kwargs):
    sig = inspect.signature(func)
    return {k: v for k, v in kwargs.items() if k in sig.parameters}

# ----------------------------------------------------------------------

class TensorHeomApp(ctk.CTk):
    def __init__(self):
        """ This window is the main window. """

        super().__init__()
        self.title("TensorHEOM")

        # parameters
        self.kwargs = {}
        self.num_qubits = 2
        self.qc = None
        self.qc_filename = "development/circuit.qpy"

        # calculation 
        self.submissionParams, self.job_id = {}, "" # with HPC
        self.result_filename = "development/result.csv" # without HPC
        self.t_list = None
        self.dm_list = None

        # plotting
        self.plot_kwargs = {} 

        # Configure the grid layout for the root window
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=1)

        self.grid_rowconfigure(0, weight=5)
        self.grid_rowconfigure(1, weight=1)

        # --------------------------------------------------------------

        # left frames
        self.left_frame = LeftFrame(self)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.help_frame = HelpFrame(self)
        self.help_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # --------------------------------------------------------------

        # middle frames
        self.middle_frame = MiddleFrame(self)
        self.middle_frame.grid(row=0, column=1, rowspan=3, padx=10, pady=10, sticky="nsew")

        # --------------------------------------------------------------

        # right frames
        self.right_frame = RightFrame(self)
        self.right_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        self.console_frame = ScrollableConsoleFrame(self)
        self.console_frame.grid(row=1, column=2, padx=10, pady=10, rowspan=2, sticky="nsew")

        # --------------------------------------------------------------

        self.middle_frame.change_state("disabled")
        self.right_frame.change_state1("disabled")
        self.right_frame.change_state2("disabled")

    # ------------------------------------------------------------------
    # help frame functions
    # ------------------------------------------------------------------

    def open_github(self):
        webbrowser.open("https://github.com/dehe1011")

    def open_paper(self):
        webbrowser.open("http://arxiv.org/abs/2510.05872")

    def open_help_window(self):
        print("Opening help window...")
        popup = HelpWindow(self)
        popup.grab_set()
        self.wait_window(popup)

    # ------------------------------------------------------------------
    # left frame functions
    # ------------------------------------------------------------------

    def open_circuit_editor(self):
        self.kwargs = self.left_frame.get_kwargs()
        self.num_qubits = self.kwargs['numQ']

        # modifies self.qc
        print("Opening circuit editor window...")
        popup = CircuitEditor(self)
        popup.grab_set()
        self.wait_window(popup)
        print(f"Circuit built successfully and saved as {self.qc_filename}")

        self.continue_to_middle_frame()

    def upload_circuit(self):
        self.kwargs = self.left_frame.get_kwargs()
        self.num_qubits = self.kwargs['numQ']

        # modifies self.qc
        print("Uploading circuit...")
        filepath = filedialog.askopenfilename(filetypes=[("QPY files", "*.qpy")])
        with open(filepath, "rb") as f:
            circuits = qpy.load(f)
        self.qc = circuits[0]
        print("Info: Circuit uploaded successfully.")

        self.continue_to_middle_frame()

    def continue_to_middle_frame(self):

        if self.kwargs['architecture'] == 'ladder':
            print('Warning: ladder architecture is not yet supported.')
            return
        
        if self.qc is None:
            print("Please define a quantum circuit to continue.")
            return 
        
        if self.qc.num_qubits != self.num_qubits:
            print(f"Warning: Uploaded circuit has {self.qc.num_qubits} qubits, but {self.num_qubits} were specified. Using {self.qc.num_qubits} qubits.")
            self.num_qubits = self.qc.num_qubits
            self.kwargs['numQ'] = self.num_qubits

        # set default initial state
        self.kwargs['rhoIni'] = q.tensor( [q.fock_dm(2,0) for _ in range(self.num_qubits)] ).full().real

        # enable middle frame
        self.left_frame = LeftFrame(self)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.left_frame.change_state("disabled")
        self.middle_frame = MiddleFrame(self)
        self.middle_frame.grid(
            row=0, column=1, rowspan=3, padx=10, pady=10, sticky="nsew"
        )

    # ------------------------------------------------------------------
    # middle frame functions
    # ------------------------------------------------------------------

    def open_state_editor(self):

        # modifies self.init_state
        print("Opening state editor window...")
        popup = StateEditor(self)
        popup.grab_set()
        self.wait_window(popup)

    def back_to_left_frame(self):
        self.right_frame.change_state1("disabled")
        self.right_frame.change_state2("disabled")
        self.middle_frame.change_state("disabled")
        self.left_frame.change_state("normal")

    def continue_to_right_frame(self):
        """ Proceed to right frame and prepare kwargs for calculation. """

        # update kwargs
        self.kwargs.update(self.middle_frame.get_kwargs())
        self.kwargs['V'] = np.array([[[0, 1],[1, 0]] for _ in range(self.num_qubits)], dtype=np.complex128)
        self.kwargs['stride'] = int(self.kwargs['strideTime'] / self.kwargs['dtFB']) 

        # rho
        self.kwargs['rho'] = {
            'numQ': self.kwargs['numQ'], 
            'rhoIni': self.kwargs['rhoIni'], 
            'omegaQ': self.kwargs['omegaQ'],
            }

        # gateList
        kwargs1Q = [{'omega': -self.kwargs['omegaQ'][i], 'gateTime': self.kwargs['gate_time'][i]} for i in range(self.num_qubits) ]
        kwargs2Q = {'gateTime': self.kwargs['gate_time'][0]/2}
        gateList1Q = [[[i], 'rxyStep', kwargs1Q[i]] for i in range(self.num_qubits)]
        gateList2Q = [[[i, i+1], 'directCplStepVarJ', kwargs2Q] for i in range(self.num_qubits - 1)]
        self.kwargs['gateList'] = gateList1Q + gateList2Q

        print(self.kwargs)

        # enable right frame
        self.middle_frame.change_state("disabled")
        self.right_frame.change_state1("normal")

    # ------------------------------------------------------------------
    # right frame functions
    # ------------------------------------------------------------------

    def upload_file(self):
        """Upload result file (calculation either on HPC or locally)."""

        print("Uploading result file...")
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        self.t_list, self.dm_list = loadResult(filepath)
        print("Info: Result file uploaded successfully.")

        # enable lower right frame
        self.right_frame.change_state2("normal")

    def submit_local(self):
        """Submit local calculation job."""

        t0 = time.time()
        filtered = filter_kwargs(main, self.kwargs)
        main(self.result_filename, self.qc, **filtered)
        self.t_list, self.dm_list = loadResult(self.result_filename)
        print(f"Calculation finished in {time.time()-t0}s. Saved as {self.result_filename}.")

        # enable lower right frame
        self.right_frame.change_state2("normal")

    def submit_hpc(self):
        """Submit calculation job to HPC."""

        # modify submissionParams
        print("Opening HPC Settings window...")
        popup = HPCSettings(self)
        popup.grab_set()
        self.wait_window(popup)

        # submit job
        print("Submitting job to HPC...")
        filtered = filter_kwargs(submitJob, self.kwargs)
        self.job_id = submitJob(self.submissionParams, self.qc, **filtered)

    def download_file(self):
        """Download result file from HPC."""

        print("Opening HPC Download window...")
        popup = HPCDownload(self)
        popup.grab_set()
        self.wait_window(popup)

        self.t_list, self.dm_list = loadResult(self.job_id + ".csv")
        print(f"Info: Result file downloaded successfully and saved as {self.job_id}.csv.")

        # enable lower right frame
        self.right_frame.change_state2("normal")

    def back_to_middle_frame(self):
        """Go back to middle frame."""

        self.t_list = None
        self.dm_list = None
    
        self.right_frame.change_state1("disabled")
        self.right_frame.change_state2("disabled")
        self.middle_frame.change_state("normal")
        self.left_frame.change_state("disabled")

    # ------------------------------------------------------------------
    # plotting window functions
    # ------------------------------------------------------------------

    def calculate_fidelity(self):
        """Fidelity calculation."""

        rho = self.dm_list[-1]

        U = Operator(self.qc).data
        rhoIni = self.kwargs['rhoIni']
        target = U @ rhoIni @ U.conj().T

        F = getFidelity(rho, target)
        print(f"Fidelity: {F}")
        return F

    def calculate_concurrence(self):
        """Concurrence calculation for 2 qubits only."""

        if not self.num_qubits == 2:
            print("Concurrence is only defined for 2 qubits.")
            return None
    
        rho = self.dm_list[-1]

        C = getConcurrence(rho)
        print(f"Concurrence: {C}")
        return C
    
    def plot(self):  
        """Plotting window."""
        self.plot_kwargs = self.right_frame.get_kwargs()
        PlottingWindow(self)

# ----------------------------------------------------------------------
