import customtkinter as ctk

from ..gui_utils import (
    change_state_all_widgets, Counter,
    make_section_label, make_labeled_entry,
    BTN_WIDTH_PRIMARY, BTN_WIDTH_SECONDARY, PAD_OUTER, PAD_Y,
)

# ----------------------------------------------------------------------


class LeftFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=10)
        self.master = master
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        row = 0

        # ── section: Circuit ─────────────────────────────────────────────
        rows_used = make_section_label(self, "Circuit", row, colspan=2)
        row += rows_used

        ctk.CTkLabel(
            self, text="Number of qubits:", font=ctk.CTkFont(size=12), anchor="w"
        ).grid(row=row, column=0, padx=PAD_OUTER, pady=PAD_Y, sticky="w")
        self.num_qubits_counter = Counter(
            self, start=self.master.numQ, minimum=1, maximum=9
        )
        self.num_qubits_counter.grid(
            row=row, column=1, padx=PAD_OUTER, pady=PAD_Y, sticky="e"
        )
        row += 1

        self.circuit_editor_button = ctk.CTkButton(
            self,
            text="Open Circuit Editor",
            width=BTN_WIDTH_PRIMARY,
            command=master.open_circuit_editor,
        )
        self.circuit_editor_button.grid(
            row=row, column=0, columnspan=2, padx=PAD_OUTER, pady=(PAD_Y, 2),
            sticky="ew",
        )
        row += 1

        self.circuit_upload_button = ctk.CTkButton(
            self,
            text="Upload Circuit (.qpy)",
            width=BTN_WIDTH_PRIMARY,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            command=master.upload_circuit,
        )
        self.circuit_upload_button.grid(
            row=row, column=0, columnspan=2, padx=PAD_OUTER, pady=(2, PAD_Y),
            sticky="ew",
        )
        row += 1

        # ── spacer ───────────────────────────────────────────────────────
        self.grid_rowconfigure(row, weight=1)
        row += 1

        # ── section: Output ──────────────────────────────────────────────
        rows_used = make_section_label(self, "Output", row, colspan=2)
        row += rows_used

        ctk.CTkLabel(
            self, text="Directory:", font=ctk.CTkFont(size=12), anchor="w"
        ).grid(row=row, column=0, padx=PAD_OUTER, pady=PAD_Y, sticky="w")
        self.directory_entry = ctk.CTkEntry(self, width=120)
        self.directory_entry.insert(0, self.master.directory_display)
        self.directory_entry.grid(
            row=row, column=1, padx=PAD_OUTER, pady=PAD_Y, sticky="ew"
        )
        row += 1

        ctk.CTkLabel(
            self, text="Filename:", font=ctk.CTkFont(size=12), anchor="w"
        ).grid(row=row, column=0, padx=PAD_OUTER, pady=PAD_Y, sticky="w")
        self.filename_entry = ctk.CTkEntry(self, width=120)
        self.filename_entry.insert(0, self.master.fileName)
        self.filename_entry.grid(
            row=row, column=1, padx=PAD_OUTER, pady=PAD_Y, sticky="ew"
        )
        row += 1

        # ── spacer ───────────────────────────────────────────────────────
        self.grid_rowconfigure(row, weight=1)
        row += 1

        # ── continue button ───────────────────────────────────────────────
        self.continue_button = ctk.CTkButton(
            self,
            text="Continue →",
            width=BTN_WIDTH_PRIMARY,
            command=master.continue_to_middle_frame,
        )
        self.continue_button.grid(
            row=row, column=0, columnspan=2, padx=PAD_OUTER, pady=PAD_OUTER,
            sticky="ew",
        )

    # ------------------------------------------------------------------

    def get_args(self):
        directory = self.directory_entry.get()
        filename = self.filename_entry.get()
        numQ = int(self.num_qubits_counter.get())
        return directory, filename, numQ

    def change_state(self, state):
        change_state_all_widgets(self, state=state)

# ----------------------------------------------------------------------
