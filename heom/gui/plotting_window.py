import os

import numpy as np
import customtkinter as ctk
import matplotlib.pyplot as plt
from qiskit.quantum_info import Operator
from scipy.linalg import eigvals
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ----------------------------------------------------------------------

class PlottingFrame(ctk.CTkFrame):
    def __init__(self, master):

        # initialization of the ctk.CTkFrame class
        super().__init__(master)

        # widgets
        self.filename_label = ctk.CTkLabel(self, text="Filename:")
        self.filename_label.grid(row=0, column=0, pady=10, padx=10)

        self.filename_entry = ctk.CTkEntry(self)
        self.filename_entry.grid(row=1, column=0, padx=10, pady=10)

        self.directory_label = ctk.CTkLabel(self, text="Directory:")
        self.directory_label.grid(row=0, column=1, pady=10, padx=10)

        self.directory_entry = ctk.CTkEntry(self)
        self.directory_entry.grid(row=1, column=1, padx=10, pady=10)

        self.subframe = ctk.CTkFrame(self)
        self.subframe.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.save_button = ctk.CTkButton(self, text="Save", command=master.save)
        self.save_button.grid(row=4, column=0, padx=10, pady=10)

        self.cancel_button = ctk.CTkButton(self, text="Cancel", command=master.cancel)
        self.cancel_button.grid(row=4, column=1, padx=10, pady=10)

class PlottingWindow(ctk.CTkToplevel):
    def __init__(self, master):

        # initialization of the ctk.CTkToplevel class
        super().__init__(master)
        self.title("Plotting")
        self.controller = master

        self.plotting_frame = PlottingFrame(self)
        self.plotting_frame.grid(
            row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"
        )

        if self.controller.plot_kwargs['plot_type'] == 'Density matrix':
            self.plot_dm()

        if self.controller.plot_kwargs['plot_type'] == 'Fidelity':
            self.plot_fidelity()
        
        if self.controller.plot_kwargs['plot_type'] == 'Concurrence':
            if not self.controller.kwargs['numQ'] == 2:
                print("Concurrence is only defined for 2 qubits.")
                return
            else:
                self.plot_concurrence()

        self.plotting(self.fig)

    # ------------------------------------------------------------------

    def plot_concurrence(self):
                  
        sigma_y = np.array([[0, -1j], [1j, 0]])
        Y = np.kron(sigma_y, sigma_y)

        concs = []
        for rho in self.controller.dm_list:
            rho_tilde = Y @ rho.conj() @ Y
            R = rho @ rho_tilde
            eigenvals = np.sort(np.sqrt(np.abs(eigvals(R))))[::-1]
            C = max(0, eigenvals[0] - sum(eigenvals[1:]))
            concs.append(C)

        self.fig, self.ax = plt.subplots()
        self.ax.plot(self.controller.t_list, concs)
        self.ax.set_xlabel("Time [ns]")
        self.ax.set_ylabel("Concurrence")
        self.ax.set_ylim(0, 1.05)

    def plot_fidelity(self):
        U = Operator(self.controller.qc).data
        target = U @ self.controller.rho['rhoIni'] @ U.conj().T
        fids = [np.real(np.trace(rho @ target)) for rho in self.controller.dm_list]

        self.fig, self.ax = plt.subplots()
        self.ax.plot(self.controller.t_list, fids)
        self.ax.set_xlabel("Time [ns]")
        self.ax.set_ylabel("Fidelity")
        self.ax.set_ylim(0, 1.05)

    def plot_dm(self):
        dim = self.controller.dm_list[0].shape[0]
        self.fig, self.ax = plt.subplots(dim, dim, figsize=(dim*1.7, dim*1.05), sharex=True, sharey=True)
        for i in range(dim):
            for j in range(dim):
                self.ax[i,j].plot(self.controller.t_list, [dm[i,j].real for dm in self.controller.dm_list])
                self.ax[i,j].plot(self.controller.t_list, [dm[i,j].imag for dm in self.controller.dm_list])
                self.ax[i,j].plot(self.controller.t_list, [np.abs(dm[i,j]) for dm in self.controller.dm_list])

                self.ax[i,j].set_yticks([-1, -0.5, 0, 0.5, 1])
        for j in range(dim):
            self.ax[-1,j].set_xlabel("Time [ns]")
        self.ax[0,0].legend(['Re', 'Im', 'Abs'], loc='upper right', fontsize=5)

    # ------------------------------------------------------------------

    def save(self):
        filename = self.plotting_frame.filename_entry.get()
        directory = self.plotting_frame.directory_entry.get()
        filepath = os.path.join(directory, filename)
        self.fig.savefig(filepath)
        self.destroy()

    def cancel(self):
        self.destroy()

    def plotting(self, fig):
        for widget in self.plotting_frame.subframe.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.plotting_frame.subframe)
        canvas.draw()
        canvas.get_tk_widget().pack()


# ----------------------------------------------------------------------