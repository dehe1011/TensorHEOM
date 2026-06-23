import customtkinter as ctk

# ----------------------------------------------------------------------
# Theme constants — single source of truth for all GUI styling
# ----------------------------------------------------------------------

FONT_TITLE  = ("Segoe UI", 15, "bold")
FONT_HEADER = ("Segoe UI", 13, "bold")
FONT_LABEL  = ("Segoe UI", 12)
FONT_SMALL  = ("Segoe UI", 11)
FONT_MONO   = ("Courier New", 11)

PAD_OUTER = 12   # outer frame padding
PAD_INNER = 8    # inner widget padding
PAD_Y     = 6    # vertical padding between rows

BTN_WIDTH_PRIMARY   = 180
BTN_WIDTH_SECONDARY = 130
BTN_WIDTH_SMALL     = 80

ENTRY_WIDTH = 200

SECTION_COLOR_LIGHT = "#e8eaed"
SECTION_COLOR_DARK  = "#2b2d30"

# ----------------------------------------------------------------------

def change_state_all_widgets(frame, state):
    for widget in frame.winfo_children():
        if isinstance(widget, (ctk.CTkFrame, ctk.CTkScrollableFrame)):
            change_state_all_widgets(widget, state)
        elif isinstance(widget, ctk.CTkBaseClass) and not isinstance(widget, ctk.CTkLabel):
            try:
                widget.configure(state=state)
            except Exception:
                pass


def make_section_label(parent, text, row, colspan=2):
    """Render a bold section header spanning the full frame width."""
    lbl = ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont(size=13, weight="bold"),
        anchor="w",
    )
    lbl.grid(row=row, column=0, columnspan=colspan, padx=PAD_OUTER,
             pady=(PAD_OUTER, 2), sticky="w")
    sep = ctk.CTkFrame(parent, height=2, fg_color=("gray70", "gray40"))
    sep.grid(row=row + 1, column=0, columnspan=colspan, padx=PAD_OUTER,
             pady=(0, PAD_Y), sticky="ew")
    return 2   # rows consumed


def make_labeled_entry(parent, label_text, row, default="",
                        entry_width=ENTRY_WIDTH, show=None):
    """Add a label + entry pair and return the entry widget."""
    lbl = ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=12),
                       anchor="w")
    lbl.grid(row=row, column=0, padx=PAD_OUTER, pady=PAD_Y, sticky="w")
    kw = {"width": entry_width}
    if show is not None:
        kw["show"] = show
    entry = ctk.CTkEntry(parent, **kw)
    entry.insert(0, str(default))
    entry.grid(row=row, column=1, padx=PAD_OUTER, pady=PAD_Y, sticky="ew")
    return entry


# ----------------------------------------------------------------------

class Counter(ctk.CTkFrame):
    """Compact +/− integer counter widget."""

    def __init__(self, master=None, start=1, minimum=1, maximum=9):
        super().__init__(master, fg_color="transparent")
        self.value = start
        self.min_val = minimum
        self.max_val = maximum

        self._decrease_btn = ctk.CTkButton(
            self, text="−", width=32, height=28,
            font=ctk.CTkFont(size=14),
            command=self._decrease,
        )
        self._decrease_btn.pack(side="left", padx=2)

        self._label = ctk.CTkLabel(
            self, text=str(self.value), width=36,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._label.pack(side="left", padx=2)

        self._increase_btn = ctk.CTkButton(
            self, text="+", width=32, height=28,
            font=ctk.CTkFont(size=14),
            command=self._increase,
        )
        self._increase_btn.pack(side="left", padx=2)

    def _increase(self):
        if self.value < self.max_val:
            self.value += 1
            self._label.configure(text=str(self.value))

    def _decrease(self):
        if self.value > self.min_val:
            self.value -= 1
            self._label.configure(text=str(self.value))

    def get(self):
        return self.value

    def configure(self, state=None, **kwargs):
        if state is not None:
            self._increase_btn.configure(state=state)
            self._decrease_btn.configure(state=state)
        super().configure(**kwargs)


# ----------------------------------------------------------------------

class StepIndicator(ctk.CTkFrame):
    """Horizontal step-progress bar showing the 4 workflow stages."""

    STEPS = ["1 · Circuit", "2 · Parameters", "3 · Run", "4 · Results"]

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._labels: list[ctk.CTkLabel] = []
        for i, name in enumerate(self.STEPS):
            lbl = ctk.CTkLabel(
                self, text=name,
                font=ctk.CTkFont(size=11),
                width=120,
            )
            lbl.grid(row=0, column=i * 2, padx=4)
            self._labels.append(lbl)
            if i < len(self.STEPS) - 1:
                arrow = ctk.CTkLabel(
                    self, text="›", font=ctk.CTkFont(size=14),
                    text_color=("gray50", "gray60"),
                )
                arrow.grid(row=0, column=i * 2 + 1)
        self.set_step(0)

    def set_step(self, active: int):
        for i, lbl in enumerate(self._labels):
            if i < active:
                lbl.configure(
                    text_color=("gray50", "gray55"),
                    font=ctk.CTkFont(size=11),
                )
            elif i == active:
                lbl.configure(
                    text_color=("#1a73e8", "#4fa3f7"),
                    font=ctk.CTkFont(size=11, weight="bold"),
                )
            else:
                lbl.configure(
                    text_color=("gray50", "gray55"),
                    font=ctk.CTkFont(size=11),
                )

# ----------------------------------------------------------------------
