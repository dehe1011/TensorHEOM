import customtkinter as ctk

from ..gui_utils import (
    make_section_label,
    BTN_WIDTH_PRIMARY, BTN_WIDTH_SECONDARY, PAD_OUTER, PAD_Y,
)

# ----------------------------------------------------------------------


class RightFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=10)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        row = 0

        # ── section: Run ─────────────────────────────────────────────────
        row += make_section_label(self, "Run Simulation", row)

        self.submit_button = ctk.CTkButton(
            self,
            text="▶  Run Locally",
            width=BTN_WIDTH_PRIMARY,
            command=master.submit_local,
        )
        self.submit_button.grid(
            row=row, column=0, columnspan=2, padx=PAD_OUTER,
            pady=(PAD_Y, 2), sticky="ew",
        )
        row += 1

        self.load_result_button = ctk.CTkButton(
            self,
            text="Upload Result File",
            width=BTN_WIDTH_PRIMARY,
            fg_color=("gray65", "gray25"),
            hover_color=("gray55", "gray35"),
            command=master.upload_file,
        )
        self.load_result_button.grid(
            row=row, column=0, columnspan=2, padx=PAD_OUTER,
            pady=2, sticky="ew",
        )
        row += 1

        # ── HPC sub-row ──────────────────────────────────────────────────
        self.submit_hpc_button = ctk.CTkButton(
            self,
            text="Submit to HPC",
            width=BTN_WIDTH_SECONDARY,
            fg_color=("gray65", "gray25"),
            hover_color=("gray55", "gray35"),
            command=master.submit_hpc,
        )
        self.submit_hpc_button.grid(
            row=row, column=0, padx=(PAD_OUTER, 2), pady=2, sticky="ew"
        )

        self.download_button = ctk.CTkButton(
            self,
            text="Download Result",
            width=BTN_WIDTH_SECONDARY,
            fg_color=("gray65", "gray25"),
            hover_color=("gray55", "gray35"),
            command=master.download_file,
        )
        self.download_button.grid(
            row=row, column=1, padx=(2, PAD_OUTER), pady=2, sticky="ew"
        )
        row += 1

        self.back_button = ctk.CTkButton(
            self,
            text="← Back",
            width=BTN_WIDTH_PRIMARY,
            fg_color=("gray65", "gray25"),
            hover_color=("gray55", "gray35"),
            command=master.back_to_middle_frame,
        )
        self.back_button.grid(
            row=row, column=0, columnspan=2, padx=PAD_OUTER,
            pady=(2, PAD_Y), sticky="ew",
        )
        row += 1

        # ── spacer ───────────────────────────────────────────────────────
        self.grid_rowconfigure(row, weight=1)
        row += 1

        # ── section: Evaluation ──────────────────────────────────────────
        row += make_section_label(self, "Evaluation", row)

        self.plot_pulse_seq_button = ctk.CTkButton(
            self,
            text="Pulse Sequence",
            width=BTN_WIDTH_PRIMARY,
            command=master.open_plotting_pulse_window,
        )
        self.plot_pulse_seq_button.grid(
            row=row, column=0, columnspan=2, padx=PAD_OUTER,
            pady=(PAD_Y, 2), sticky="ew",
        )
        row += 1

        self.calculate_fidelity_button = ctk.CTkButton(
            self,
            text="Calculate Fidelity",
            width=BTN_WIDTH_SECONDARY,
            command=master.calculate_fidelity,
        )
        self.calculate_fidelity_button.grid(
            row=row, column=0, padx=(PAD_OUTER, 2), pady=2, sticky="ew"
        )

        self.calculate_concurrence_button = ctk.CTkButton(
            self,
            text="Calculate Concurrence",
            width=BTN_WIDTH_SECONDARY,
            command=master.calculate_concurrence,
        )
        self.calculate_concurrence_button.grid(
            row=row, column=1, padx=(2, PAD_OUTER), pady=2, sticky="ew"
        )
        row += 1

        # ── spacer ───────────────────────────────────────────────────────
        self.grid_rowconfigure(row, weight=1)
        row += 1

        # ── section: Plot ────────────────────────────────────────────────
        row += make_section_label(self, "Plot Results", row)

        self.plot_combobox = ctk.CTkComboBox(
            self,
            values=["RDO", "Fidelity", "Concurrence", "Logarithmic Negativity"],
            width=130,
        )
        self.plot_combobox.set("RDO")
        self.plot_combobox.grid(
            row=row, column=0, padx=(PAD_OUTER, 2), pady=PAD_Y, sticky="ew"
        )

        self.plot_button = ctk.CTkButton(
            self,
            text="Plot",
            width=80,
            command=master.plot,
        )
        self.plot_button.grid(
            row=row, column=1, padx=(2, PAD_OUTER), pady=PAD_Y, sticky="ew"
        )
        row += 1

        # ── bottom spacer ─────────────────────────────────────────────────
        self.grid_rowconfigure(row, weight=1)

    # ------------------------------------------------------------------

    def get_args(self):
        return self.plot_combobox.get()

    def change_state1(self, state):
        for w in (
            self.load_result_button,
            self.download_button,
            self.submit_button,
            self.submit_hpc_button,
            self.back_button,
            self.plot_pulse_seq_button,
        ):
            w.configure(state=state)

    def change_state2(self, state):
        for w in (
            self.calculate_fidelity_button,
            self.calculate_concurrence_button,
            self.plot_combobox,
            self.plot_button,
        ):
            w.configure(state=state)

# ----------------------------------------------------------------------
