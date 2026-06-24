import numpy as np
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from qiskit.quantum_info import Operator
from tkinter import filedialog

from ..gui_utils import PAD_OUTER, PAD_Y
from ...evaluation import getConcurrence, getFidelity, getLogarithmicNegativity

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
            if self.master.numQ != 2:
                print("Concurrence is only defined for 2 qubits.")
                return 
            else:
                self._plot_concurrence()
        elif plot_type == "Logarithmic Negativity":
            if self.master.numQ < 2:
                print("Logarithmic Negativity is only defined for 2 or more qubits.")
                return 
            else:
                self._plot_logarithmic_negativity()

        if self.fig is not None:
            self._embed_figure()

    # ------------------------------------------------------------------

    def _embed_figure(self):
        # Clear old widgets
        for widget in self._canvas_frame.winfo_children():
            widget.destroy()

        # Separate frames: toolbar and canvas must not mix pack/grid
        toolbar_frame = ctk.CTkFrame(self._canvas_frame, fg_color="transparent")
        toolbar_frame.grid(row=0, column=0, sticky="ew")

        canvas_frame = ctk.CTkFrame(self._canvas_frame, fg_color="transparent")
        canvas_frame.grid(row=1, column=0, sticky="nsew")

        self._canvas_frame.grid_rowconfigure(0, weight=0)
        self._canvas_frame.grid_rowconfigure(1, weight=1)
        self._canvas_frame.grid_columnconfigure(0, weight=1)

        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        canvas.draw()

        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew")

        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=0, column=0, sticky="w")

        self.canvas = canvas
        self.toolbar = toolbar

    def _plot_concurrence(self):

        concs = [getConcurrence(rho) for rho in self.master.dm_list]

        self.fig, ax = plt.subplots(figsize=(6, 3.5), tight_layout=True)
        ax.plot(self.master.t_list, concs, linewidth=1.8)
        ax.set_xlabel("t [ns]")
        ax.set_ylabel("C")
        ax.set_ylim(-0.02, 1.02)
        ax.grid(True, alpha=0.3)

    def _plot_logarithmic_negativity(self):
        # TODO: always wrt first qubit, or allow user to select qubit?
        log_neg = [getLogarithmicNegativity(rho, transposeQIdx=[0]) for rho in self.master.dm_list]

        self.fig, ax = plt.subplots(figsize=(6, 3.5), tight_layout=True)
        ax.plot(self.master.t_list, log_neg, linewidth=1.8)
        ax.set_xlabel("t [ns]")
        ax.set_ylabel("E_N")
        ax.set_ylim(-0.02, max(log_neg) + 0.1)
        ax.grid(True, alpha=0.3) 

    def _plot_fidelity(self):
        U = Operator(self.master.kwargs["qc"]).data
        target = U @ self.master.kwargs["rhoIni"] @ U.conj().T

        fids = [getFidelity(rho, target) for rho in self.master.dm_list]

        self.fig, ax = plt.subplots(figsize=(6, 3.5), tight_layout=True)
        ax.plot(self.master.t_list, fids, linewidth=1.8)
        ax.set_xlabel("t [ns]")
        ax.set_ylabel("F")
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
            axes[-1, j].set_xlabel("t [ns]", fontsize=8)
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
