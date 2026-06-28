import os
from tkinter import filedialog

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from ..gui_utils import PAD_OUTER


class PlottingPulseWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.fig_circ = None
        self.fig_pulse = None
        self.canvas_circ = None
        self.canvas_pulse = None

        self.title("Circuit and Pulse Sequence")
        self.title("Circuit and Pulse Sequence")
        self.geometry("760x620")
        self.minsize(640, 500)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=2)

        # ── toolbar row ─────────────────────────────────────────────────
        toolbar_frame = ctk.CTkFrame(self, fg_color="transparent")
        toolbar_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=PAD_OUTER,
            pady=(PAD_OUTER, 0),
        )
        toolbar_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            toolbar_frame,
            text="Circuit and Pulse Sequence",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            toolbar_frame,
            text="Save Circuit",
            width=110,
            command=lambda: self._save_figure(self.fig_circ, "circuit.png"),
        ).grid(row=0, column=2, padx=(4, 0))

        ctk.CTkButton(
            toolbar_frame,
            text="Save Pulse",
            width=110,
            command=lambda: self._save_figure(self.fig_pulse, "pulse_sequence.png"),
        ).grid(row=0, column=3, padx=(4, 0))

        ctk.CTkButton(
            toolbar_frame,
            text="Close",
            width=80,
            fg_color=("gray65", "gray25"),
            hover_color=("gray55", "gray35"),
            command=self.destroy,
        ).grid(row=0, column=4, padx=(4, 0))

        # ── circuit frame ────────────────────────────────────────────────
        self._circ_outer = ctk.CTkFrame(self)
        self._circ_outer.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=PAD_OUTER,
            pady=(6, 4),
        )
        self._circ_outer.grid_columnconfigure(0, weight=1)
        self._circ_outer.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self._circ_outer,
            text="Quantum circuit",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=8, pady=(6, 2))

        self._circ_canvas_frame = ctk.CTkFrame(self._circ_outer, fg_color="transparent")
        self._circ_canvas_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self._circ_canvas_frame.grid_columnconfigure(0, weight=1)
        self._circ_canvas_frame.grid_rowconfigure(0, weight=1)

        # ── pulse frame ──────────────────────────────────────────────────
        self._pulse_outer = ctk.CTkFrame(self)
        self._pulse_outer.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=PAD_OUTER,
            pady=(4, PAD_OUTER),
        )
        self._pulse_outer.grid_columnconfigure(0, weight=1)
        self._pulse_outer.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self._pulse_outer,
            text="Pulse sequence",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=8, pady=(6, 2))

        self._pulse_canvas_frame = ctk.CTkFrame(self._pulse_outer, fg_color="transparent")
        self._pulse_canvas_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self._pulse_canvas_frame.grid_columnconfigure(0, weight=1)
        self._pulse_canvas_frame.grid_rowconfigure(0, weight=1)

        # Build figures
        self.fig_circ = self.master.qc.draw(output="mpl")
        self.fig_pulse, _ = self.master.plot_pulse_seq()

        self._embed_figure(self.fig_circ, self._circ_canvas_frame, is_circuit=True)
        self._embed_figure(self.fig_pulse, self._pulse_canvas_frame, is_circuit=False)

    # ------------------------------------------------------------------

    def _embed_figure(self, fig, parent, is_circuit: bool = False):
        for widget in parent.winfo_children():
            widget.destroy()

        toolbar_frame = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar_frame.grid(row=0, column=0, sticky="ew")

        canvas_frame = ctk.CTkFrame(parent, fg_color="transparent")
        canvas_frame.grid(row=1, column=0, sticky="nsew")

        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=0)
        parent.grid_rowconfigure(1, weight=1)

        canvas_frame.grid_columnconfigure(0, weight=1)
        canvas_frame.grid_rowconfigure(0, weight=1)

        if is_circuit:
            fig.set_size_inches(6.2, 1.4)

        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw()

        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew")

        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=0, column=0, sticky="w")

        if is_circuit:
            self.canvas_circ = canvas
        else:
            self.canvas_pulse = canvas

    def _save_figure(self, fig, default_name: str):
        if fig is None:
            print("No figure available to save.")
            return

        initialdir = getattr(self.master, "directory", os.getcwd())
        path = filedialog.asksaveasfilename(
            initialdir=initialdir,
            initialfile=default_name,
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg"),
                ("All files", "*.*"),
            ],
        )

        if not path:
            return

        fig.savefig(path, bbox_inches="tight")
        print(f"Figure saved as {path}")