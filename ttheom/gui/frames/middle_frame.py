import ast
import customtkinter as ctk

from ..gui_utils import (
    change_state_all_widgets,
    make_section_label, make_labeled_entry,
    BTN_WIDTH_PRIMARY, BTN_WIDTH_SECONDARY, PAD_OUTER, PAD_Y, ENTRY_WIDTH,
)

# ----------------------------------------------------------------------


class MiddleFrame(ctk.CTkScrollableFrame):
    """Scrollable parameter panel — gates, bath, and simulation settings."""

    def __init__(self, master):
        super().__init__(master, corner_radius=10, label_text="")
        self.master = master
        self.grid_columnconfigure(0, weight=1, minsize=170)
        self.grid_columnconfigure(1, weight=1, minsize=170)
        row = 0

        # ── section: Gates ───────────────────────────────────────────────
        row += make_section_label(self, "Gates", row)

        self.qubit_frequency_entry = make_labeled_entry(
            self, "Qubit frequency (GHz):", row,
            default=str([5] * self.master.numQ),
        )
        row += 1

        self.idling_time_entry = make_labeled_entry(
            self, "Idling time (ns):", row, default="1"
        )
        row += 1

        self.oneq_gate_time_entry = make_labeled_entry(
            self, "1Q gate time (ns):", row,
            default=str([16] * self.master.numQ),
        )
        row += 1

        self.twoq_gate_time_entry = make_labeled_entry(
            self, "2Q gate time (ns):", row,
            default=str([50] * max(self.master.numQ - 1, 0)),
        )
        row += 1

        # ── spacer ───────────────────────────────────────────────────────
        self.grid_rowconfigure(row, minsize=8)
        row += 1

        # ── section: Bath ────────────────────────────────────────────────
        row += make_section_label(self, "Bath", row)

        self.T1_time_entry = make_labeled_entry(
            self, "T₁ relaxation time (µs):", row, default="32"
        )
        row += 1

        self.temperature_entry = make_labeled_entry(
            self, "Temperature (mK):", row, default="30"
        )
        row += 1

        self.omegaC_entry = make_labeled_entry(
            self, "Cutoff frequency:", row, default="20"
        )
        row += 1

        self.exponent_entry = make_labeled_entry(
            self, "Spectral exponent:", row, default="0.125"
        )
        row += 1

        self.tol_entry = make_labeled_entry(
            self, "AAA tolerance:", row, default="1e-4"
        )
        row += 1

        # ── spacer ───────────────────────────────────────────────────────
        self.grid_rowconfigure(row, minsize=8)
        row += 1

        # ── section: Simulation ──────────────────────────────────────────
        row += make_section_label(self, "Simulation", row)

        ctk.CTkLabel(
            self, text="Initial state:", font=ctk.CTkFont(size=12), anchor="w"
        ).grid(row=row, column=0, padx=PAD_OUTER, pady=PAD_Y, sticky="w")
        self.initial_state_button = ctk.CTkButton(
            self,
            text="Open State Editor",
            width=BTN_WIDTH_SECONDARY,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            command=master.open_state_editor,
        )
        self.initial_state_button.grid(
            row=row, column=1, padx=PAD_OUTER, pady=PAD_Y, sticky="ew"
        )
        row += 1

        self.dtFB_entry = make_labeled_entry(
            self, "Time step (ps):", row, default="3"
        )
        row += 1

        self.depth_entry = make_labeled_entry(
            self, "Hierarchy depth:", row, default="1"
        )
        row += 1

        self.bondDim_entry = make_labeled_entry(
            self, "Bond dimension:", row, default="5"
        )
        row += 1

        self.strideTime_entry = make_labeled_entry(
            self, "Output interval (ns):", row, default="0.1"
        )
        row += 1

        # ── checkboxes ───────────────────────────────────────────────────
        self.useRFPlus_var = ctk.BooleanVar(value=False)
        self.useRFPlus_checkbox = ctk.CTkCheckBox(
            self, text="Use Redfield+ (RF+)",
            variable=self.useRFPlus_var,
            font=ctk.CTkFont(size=12),
        )
        self.useRFPlus_checkbox.grid(
            row=row, column=0, padx=PAD_OUTER, pady=PAD_Y, sticky="w"
        )

        self.RK13_var = ctk.BooleanVar(value=False)
        self.RK13_checkbox = ctk.CTkCheckBox(
            self, text="Use RK13",
            variable=self.RK13_var,
            font=ctk.CTkFont(size=12),
        )
        self.RK13_checkbox.grid(
            row=row, column=1, padx=PAD_OUTER, pady=PAD_Y, sticky="w"
        )
        row += 1

        # ── spacer ───────────────────────────────────────────────────────
        self.grid_rowconfigure(row, minsize=8)
        row += 1

        # ── nav buttons ──────────────────────────────────────────────────
        self.back_button = ctk.CTkButton(
            self,
            text="← Back",
            width=BTN_WIDTH_SECONDARY,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            command=master.back_to_left_frame,
        )
        self.back_button.grid(
            row=row, column=0, padx=PAD_OUTER, pady=PAD_OUTER, sticky="ew"
        )

        self.continue_button = ctk.CTkButton(
            self,
            text="Continue →",
            width=BTN_WIDTH_SECONDARY,
            command=master.continue_to_right_frame,
        )
        self.continue_button.grid(
            row=row, column=1, padx=PAD_OUTER, pady=PAD_OUTER, sticky="ew"
        )

    # ------------------------------------------------------------------

    def get_args(self):
        freqQ        = ast.literal_eval(self.qubit_frequency_entry.get())
        gateTimeOneQ = ast.literal_eval(self.oneq_gate_time_entry.get())
        gateTimeTwoQ = ast.literal_eval(self.twoq_gate_time_entry.get())
        gateTime     = gateTimeOneQ + gateTimeTwoQ
        T            = float(self.temperature_entry.get())
        T1           = float(self.T1_time_entry.get())
        omegaC       = float(self.omegaC_entry.get())
        exp          = float(self.exponent_entry.get())
        tol          = float(self.tol_entry.get())
        idlingTime   = float(self.idling_time_entry.get())
        depth        = [int(self.depth_entry.get())] * self.master.numQ
        dtFB         = float(self.dtFB_entry.get())
        bondDim      = int(self.bondDim_entry.get())
        strideTime   = float(self.strideTime_entry.get())
        useRFPlus    = self.useRFPlus_var.get()
        isRK13       = self.RK13_var.get()
        return (freqQ, gateTime, T, T1, omegaC, exp, tol,
                idlingTime, dtFB, depth, bondDim, strideTime, useRFPlus, isRK13)

    def change_state(self, state):
        change_state_all_widgets(self, state=state)
        self.continue_button.configure(state=state)

# ----------------------------------------------------------------------
