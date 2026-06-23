import os

import numpy as np
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from qiskit.quantum_info import Operator
from scipy.linalg import eigvals
from tkinter import filedialog

from ..gui_utils import PAD_OUTER, PAD_Y

# ----------------------------------------------------------------------


class PlottingWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.fig = None

        plot_type = self.master.plot_kwargs.get("plot_type", "RDO")
        self.title(f"Plot — {plot_type}")
        self.geometry("700x560")
        self.minsize(600, 480)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── toolbar row ───────────────────────────────────────────────────
        toolbar_frame = ctk.CTkFrame(self, fg_color="transparent")
        toolbar_frame.grid(row=0, column=0, sticky="ew", padx=PAD_OUTER, pady=(PAD_OUTER, 0))
        toolbar_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            toolbar_frame,
            text=f"Plot: {plot_type}",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            toolbar_frame,
            text="Save Figure",
            width=120,
            command=self._save,
        ).grid(row=0, column=1, padx=(4, 0))

        ctk.CTkButton(
            toolbar_frame,
            text="Close",
            width=80,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            command=self.destroy,
        ).grid(row=0, column=2, padx=(4, 0))

        # ── figure canvas ────────────────────────────────────────────────
        self._canvas_frame = ctk.CTkFrame(self)
        self._canvas_frame.grid(row=1, column=0, sticky="nsew",
                                padx=PAD_OUTER, pady=(4, PAD_OUTER))
        self._canvas_frame.grid_columnconfigure(0, weight=1)
        self._canvas_frame.grid_rowconfigure(0, weight=1)

        # Build the figure
        if plot_type == "RDO":
            self._plot_dm()
        elif plot_type == "Fidelity":
            self._plot_fidelity()
        elif plot_type == "Concurrence":
            self._plot_concurrence()

        if self.fig is not None:
            self._embed_figure()

    # ------------------------------------------------------------------

    def _embed_figure(self):
        canvas = FigureCanvasTkAgg(self.fig, master=self._canvas_frame)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, self._canvas_frame)
        toolbar.update()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def _plot_concurrence(self):
        if self.master.numQ != 2:
            print("Concurrence is only defined for 2 qubits.")
            return

        sigma_y = np.array([[0, -1j], [1j, 0]])
        Y = np.kron(sigma_y, sigma_y)
        concs = []
        for rho in self.master.dm_list:
            rho_tilde = Y @ rho.conj() @ Y
            eigenvals_sorted = np.sort(np.sqrt(np.abs(eigvals(rho @ rho_tilde))))[::-1]
            concs.append(max(0.0, eigenvals_sorted[0] - sum(eigenvals_sorted[1:])))

        self.fig, ax = plt.subplots(figsize=(6, 3.5), tight_layout=True)
        ax.plot(self.master.t_list, concs, linewidth=1.8)
        ax.set_xlabel("Time (ns)")
        ax.set_ylabel("Concurrence")
        ax.set_ylim(-0.02, 1.02)
        ax.grid(True, alpha=0.3)

    def _plot_fidelity(self):
        U = Operator(self.master.kwargs["qc"]).data
        target = U @ self.master.kwargs["rhoIni"] @ U.conj().T
        fids = [np.real(np.trace(rho @ target)) for rho in self.master.dm_list]

        self.fig, ax = plt.subplots(figsize=(6, 3.5), tight_layout=True)
        ax.plot(self.master.t_list, fids, linewidth=1.8)
        ax.set_xlabel("Time (ns)")
        ax.set_ylabel("Fidelity")
        ax.set_ylim(-0.02, 1.02)
        ax.grid(True, alpha=0.3)

    def _plot_dm(self):
        dm_list = self.master.dm_list
        dim = dm_list[0].shape[0]
        self.fig, axes = plt.subplots(
            dim, dim, figsize=(max(dim * 2.2, 5), max(dim * 1.4, 4)),
            sharex=True, sharey=True, tight_layout=True,
        )
        if dim == 1:
            axes = np.array([[axes]])

        t = self.master.t_list
        for i in range(dim):
            for j in range(dim):
                ax = axes[i, j]
                re  = [rho[i, j].real for rho in dm_list]
                im  = [rho[i, j].imag for rho in dm_list]
                ab  = [abs(rho[i, j])  for rho in dm_list]
                ax.plot(t, re, linewidth=1.2, label="Re")
                ax.plot(t, im, linewidth=1.2, label="Im")
                ax.plot(t, ab, linewidth=1.0, linestyle="--", label="|·|")
                ax.set_yticks([-1, 0, 1])
                ax.tick_params(labelsize=7)

        for j in range(dim):
            axes[-1, j].set_xlabel("t (ns)", fontsize=8)
        axes[0, 0].legend(loc="upper right", fontsize=6)

    # ------------------------------------------------------------------

    def _save(self):
        if self.fig is None:
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG image", "*.png"),
                ("PDF document", "*.pdf"),
                ("SVG image", "*.svg"),
            ],
        )
        if filepath:
            self.fig.savefig(filepath, dpi=150)
            print(f"Figure saved to {filepath}")

# ----------------------------------------------------------------------
