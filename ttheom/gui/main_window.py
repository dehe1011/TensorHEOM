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
from .windows.plotting_circ_window import PlottingCircWindow
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
        self.numQ = 2
        self.directory_display = 'simulations_GUI'
        self.directory = os.path.join(os.getcwd(), self.directory_display)
        self.fileName = "package_test"
        self.kwargs = {}

        self.qc = QuantumCircuit(self.numQ)
        self.qcFilePath = None
        self.csvFilePath = None

        self.params = {}

        # calculation 
        self.submissionParams, self.job_id = {}, "" # with HPC
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

        # self.middle_frame.change_state("disabled")
        # self.right_frame.change_state1("disabled")
        # self.right_frame.change_state2("disabled")

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

        # get args from left frame
        self.directory, self.fileName, self.numQ = self.left_frame.get_args()
        self.qcFilePath = os.path.join(self.directory, 'qcData_' + self.fileName)

        # modifies self.qc
        print("Opening circuit editor window...")
        popup = CircuitEditor(self)
        popup.grab_set()
        self.wait_window(popup)
        print(f"Circuit built successfully and saved as {self.qcFilePath}")

    def upload_circuit(self):

        # get args from left frame
        self.directory, self.fileName, self.numQ = self.left_frame.get_args()
        self.qcFilePath = os.path.join(self.directory, 'qcData_' + self.fileName)

        # modifies self.qc
        print("Uploading circuit...")
        self.qcFilePath = filedialog.askopenfilename(filetypes=[("QPY files", "*.qpy")])
        self.qc = loadQC(self.qcFilePath)
        print("Info: Circuit uploaded successfully.")

    def continue_to_middle_frame(self):

        self.qcFilePath = os.path.join(self.directory, 'qcData_' + self.fileName)
        self.csvFilePath = os.path.join(self.directory, self.fileName + '.csv')
        
        if self.qc is None:
            print("Please define a quantum circuit to continue.")
            return 
        
        if self.qc.num_qubits != self.numQ:
            print(f"Warning: Uploaded circuit has {self.qc.num_qubits} qubits, but {self.numQ} were specified. Using {self.qc.num_qubits} qubits.")
            self.numQ = self.qc.num_qubits

        # set kwargs
        self.kwargs['directory'] = self.directory
        self.kwargs['fileName'] = self.fileName
        self.kwargs['numQ'] = self.numQ
        self.kwargs['rhoIni'] = q.tensor( [q.fock_dm(2,0) for _ in range(self.numQ)] ).full().real

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
        freqQ, gateTime, T, T1, omegaC, exp, tol, idlingTime, dtFB, depth, bondDim, useRFPlus, isRK13 = self.middle_frame.get_args()
        self.kwargs['freqQ'] = freqQ
        self.kwargs['gateTime'] = gateTime
        self.kwargs['T'] = T
        self.kwargs['T1'] = T1
        self.kwargs['omegaC'] = omegaC
        self.kwargs['exp'] = exp
        self.kwargs['tol'] = tol
        self.kwargs['idlingTime'] = idlingTime
        self.kwargs['dtFB'] = dtFB
        self.kwargs['depth'] = depth
        self.kwargs['bondDim'] = bondDim
        self.kwargs['useRFPlus'] = useRFPlus
        self.kwargs['isRK13'] = isRK13
        self.kwargs['strideTime'] = 0.1 # TODO

        self.kwargs['qc'] = self.qc

        # enable right frame
        self.middle_frame.change_state("disabled")
        self.right_frame.change_state1("normal")

    def open_plotting_pulse_window(self):
        print("Opening pulse sequence plotting window...")
        PlottingPulseWindow(self)
        PlottingCircWindow(self)
        
    def plot_pulse_seq(self):
        return plotPulseSeq(**self.kwargs)

    # ------------------------------------------------------------------
    # right frame functions
    # ------------------------------------------------------------------

    def upload_file(self):
        """Upload result file (calculation either on HPC or locally)."""

        print("Uploading result file...")
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        self.t_list, self.dm_list = loadResult(filepath)
        self.t_list /= self.params['omegaQmax']
        print("Info: Result file uploaded successfully.")

        # enable lower right frame
        self.right_frame.change_state2("normal")

    def submit_local(self):
        """Submit local calculation job."""

        t0 = time.time()
        calcTimeEvo(**self.kwargs)

        self.t_list, self.dm_list = loadResult(self.csvFilePath)
        self.t_list /= self.params['omegaQmax']
        print(f"Calculation finished in {time.time()-t0}s. Saved as {self.csvFilePath}.")

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
        stride = int(self.kwargs['strideTime'] / self.kwargs['dtFB'])
        args = prepareArgs(self.kwargs['numQ'], self.kwargs['freqQ'], self.kwargs['gateTime'], self.kwargs['T'], self.kwargs['T1'], self.wargs['omegaC'], 
            self.kwargs['exp'], self.kwargs['tol'], self.kwargs['rhoIni'], self.kwargs['idlingTime'], self.kwargs['dtFB'], self.kwargs['depth'], self.kwargs['bondDim'])
        omegaQmax, rho, bondDim, V, depth, bath, gateList, dtFB, idlingTime = args
        self.job_id = submitJob(self.submissionParams, self.qcFilePath, omegaQmax, self.kwargs['qc'], idlingTime, gateList, rho,
          bath, V, dtFB, stride, depth, bondDim, useRFPlus=self.wargs['useRFPlus'], isRK13=self.kwargs['isRK13'])

    def download_file(self):
        """Download result file from HPC."""

        print("Opening HPC Download window...")
        popup = HPCDownload(self)
        popup.grab_set()
        self.wait_window(popup)

        self.t_list, self.dm_list = loadResult(self.job_id + ".csv")
        self.t_list /= self.params['omegaQmax']
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

        if not self.numQ == 2:
            print("Concurrence is only defined for 2 qubits.")
            return None
    
        rho = self.dm_list[-1]

        C = getConcurrence(rho)
        print(f"Concurrence: {C}")
        return C
    
    def plot(self):  
        """Plotting window."""
        plot_type = self.right_frame.get_args()
        self.plot_kwargs['plot_type'] = plot_type
        PlottingWindow(self)

# ----------------------------------------------------------------------
