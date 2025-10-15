import webbrowser
import time
import os

import customtkinter as ctk
from tkinter import filedialog
import numpy as np
import qutip as q
from scipy.linalg import eigvals
from qiskit.quantum_info import Operator
from qiskit import qpy

from ..main import main
from ..ssh import submitJob

from .left_frame import LeftFrame
from .middle_frame import MiddleFrame
from .right_frame import RightFrame
from .help_frame import HelpFrame
from .scrollable_console_frame import ScrollableConsoleFrame
from .plotting_window import PlottingWindow
from .circuit_editor_window import CircuitEditor
from .state_editor_window import StateEditor
from .gui_utils import load_density_matrices
from .help_window import HelpWindow

from .hpc_settings_window import HPCSettings, HPCDownload

# --------------------------------------------------

class TensorHeomApp(ctk.CTk):
    def __init__(self):
        """ This window is the main window. """

        # initialization of the ctk.CTk class
        super().__init__()

        self.title("TensorHEOM")

        self.kwargs = {}
        self.plot_kwargs = {}
        self.num_qubits = None
        self.qc = None
        self.init_state = None
        self.fileName = "result.csv"
        self.rho = None
        self.gateList = []
        self.t_list = None
        self.dm_list = None

        self.submissionParams = {}
        self.job_id = ""

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
        self.help_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

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

        self.middle_frame.change_state("disabled")
        self.right_frame.change_state1("disabled")
        self.right_frame.change_state2("disabled")

    # ------------------------------------------------------------------

    def open_github(self):
        webbrowser.open("https://github.com/dehe1011")

    def open_paper(self):
        webbrowser.open("http://arxiv.org/abs/2510.05872")

    def submit(self): 

        useHPC = self.right_frame.HPC_var.get()
        if useHPC:
            print("Opening HPC settings window...")
            popup = HPCSettings(self)
            popup.grab_set()
            self.wait_window(popup)
            self.job_id = submitJob(self.submissionParams, self.qc, self.kwargs['idlingTime'], self.gateList, self.rho,
                                    self.kwargs['bath'], self.kwargs['V'], self.kwargs['dtFB'], self.kwargs['stride'], 
                                    depth =self.kwargs['depth'], bondDim=self.kwargs['bondDim'], 
                                    useRFPlus=self.kwargs['useRFPlus'], isRK13 = self.kwargs['isRK13'])
        
        elif self.t_list is not None and self.dm_list is not None:
            print('Info: Results already calculated and loaded.')

        elif os.path.exists("result.csv"):
            print("Warning: results.csv already exists, please rename or delete it.")
            self.t_list, self.dm_list = load_density_matrices("result.csv")

        else:
            t0 = time.time()
            main(self.fileName, self.qc, self.kwargs['idlingTime'], self.gateList, self.rho, 
                    self.kwargs['bath'], self.kwargs['V'], self.kwargs['dtFB'], self.kwargs['stride'], 
                    depth =self.kwargs['depth'], bondDim=self.kwargs['bondDim'], 
                    useRFPlus=self.kwargs['useRFPlus'], isRK13 = self.kwargs['isRK13'])
            
            self.t_list, self.dm_list = load_density_matrices("result.csv")
            print(f"Calculation finished in {time.time()-t0}s. Saved as result.csv.")

        self.right_frame.change_state2("normal")


    # ------------------------------------------------------------------

    def open_circuit_editor(self):
        self.num_qubits = self.left_frame.get_kwargs()['numQ']
        print("Opening circuit editor window...")
        popup = CircuitEditor(self, save_file="circuit.qpy")
        popup.grab_set()
        self.wait_window(popup)
        self.continue_to_middle_frame()

    def open_state_editor(self):
        print("Opening state editor window...")
        popup = StateEditor(self)
        popup.grab_set()
        self.wait_window(popup)

    def open_help_window(self):
        print("Opening help window...")
        popup = HelpWindow(self)
        popup.grab_set()
        self.wait_window(popup)

    def load_circuit(self):
        filepath = filedialog.askopenfilename(filetypes=[("QPY files", "*.qpy")])
        with open(filepath, "rb") as f:
            circuits = qpy.load(f)
        self.qc = circuits[0]
        self.num_qubits = self.qc.num_qubits
        self.left_frame.num_qubits_counter.set(str(self.num_qubits))
        print(f"Info: Circuit loaded successfully.")
        self.continue_to_middle_frame()

    def upload_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        self.t_list, self.dm_list = load_density_matrices(filepath)
        print(f"Info: Result file loaded successfully.")
        self.right_frame.change_state2("normal")

    def download_file(self):
        print("Opening HPC Download window...")
        popup = HPCDownload(self)
        popup.grab_set()
        self.wait_window(popup)
        self.t_list, self.dm_list = load_density_matrices(self.job_id + ".csv")
        print(f"Info: Result file downloaded successfully and saved as {self.job_id}.csv.")
        self.right_frame.change_state2("normal")

    def back_to_middle_frame(self):
        self.right_frame.change_state1("disabled")
        self.right_frame.change_state2("disabled")
        self.middle_frame.change_state("normal")
        self.left_frame.change_state("disabled")
        self.t_list = None
        self.dm_list = None

    def back_to_left_frame(self):
        self.right_frame.change_state1("disabled")
        self.right_frame.change_state2("disabled")
        self.middle_frame.change_state("disabled")
        self.left_frame.change_state("normal")

    def continue_to_middle_frame(self):
        self.kwargs = self.left_frame.get_kwargs()
        self.num_qubits = self.kwargs['numQ']
        
        if self.qc is None:
            print("Please define a quantum circuit to continue.")
            return 

        self.init_state = q.tensor( [q.fock_dm(2,0) for _ in range(self.num_qubits)] ).full().real
        if self.kwargs['numQ'] == 3: 
            print('Warning: 3 qubit circuits are not yet supported.')
        else:
            self.left_frame.change_state("disabled")
            self.middle_frame.change_state("normal")

    def continue_to_right_frame(self):
        self.kwargs.update(self.middle_frame.get_kwargs())

        self.kwargs['rhoIni'] = self.init_state
        self.kwargs['V'] = np.array([[[0, 1],[1, 0]] for _ in range(self.num_qubits)], dtype=np.complex128)
        self.kwargs['stride'] = int(self.kwargs['strideTime'] / self.kwargs['dtFB']) 

        # rho
        self.rho = {'numQ': self.kwargs['numQ']}
        default_rhoIni = q.tensor( [q.fock_dm(2,0) for _ in range(self.kwargs['numQ'])] ).full()
        self.rho['rhoIni'] = self.kwargs.get('rhoIni', default_rhoIni)
        self.rho['omegaQ'] = self.kwargs['omegaQ'] # * 2*np.pi  # frequency to angular frequency

        # gateList
        if self.kwargs['numQ'] == 1:
            kwargs1Q = {'omega': -self.rho['omegaQ'][0], 'gateTime': self.kwargs['gate_time']*np.pi}
            self.gateList = [[[0], 'rxyStep', kwargs1Q]]

        elif self.kwargs['numQ'] == 2:
            kwargs1Q = [{'omega': -self.rho['omegaQ'][0], 'gateTime': self.kwargs['gate_time']},
                        {'omega': -self.rho['omegaQ'][1], 'gateTime': self.kwargs['gate_time']},]
            kwargs2Q = {'gateTime': self.kwargs['gate_time']/2}
            self.gateList = [[[0], 'rxyStep', kwargs1Q[0]],
                             [[1], 'rxyStep', kwargs1Q[1]],
                             [[0, 1], 'directCplStepVarJ', kwargs2Q]]  
            
        if self.kwargs['architecture'] == 'ladder':
            print('Warning: ladder architecture is not yet supported.')
            return
        
        self.middle_frame.change_state("disabled")
        self.right_frame.change_state1("normal")
        print("Info: Ready to submit job.")

    # ------------------------------------------------------------------

    def plot(self):
        self.plot_kwargs = self.right_frame.get_kwargs()
        PlottingWindow(self)

    def calculate_fidelity(self):
        # print("Calculating fidelity...")
        rho = self.dm_list[-1]

        U = Operator(self.qc).data
        default_rhoIni = q.tensor( [q.fock_dm(2,0) for _ in range(self.kwargs['numQ'])] ).full()
        rhoIni = self.kwargs.get('rhoIni', default_rhoIni)
        target = U @ rhoIni @ U.conj().T

        F = np.real(np.trace(rho @ target))
        print(f"Fidelity: {F}")
        return F

    def calculate_concurrence(self):
        # print("Calculating concurrence...")

        if not self.kwargs['numQ'] == 2:
            print("Concurrence is only defined for 2 qubits.")
            return None
    
        rho = self.dm_list[-1]

        sigma_y = np.array([[0, -1j], [1j, 0]])
        Y = np.kron(sigma_y, sigma_y)
        rho_tilde = Y @ rho.conj() @ Y
        R = rho @ rho_tilde

        eigenvals = np.sort(np.sqrt(np.abs(eigvals(R))))[::-1]
        C = max(0, eigenvals[0] - sum(eigenvals[1:]))
        print(f"Concurrence: {C}")
        return C

# ----------------------------------------------------------------------
