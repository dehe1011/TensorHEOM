import sys
import customtkinter as ctk

from ..gui_utils import PAD_OUTER, FONT_MONO

# ----------------------------------------------------------------------


class RedirectText:
    """Redirect stdout/stderr to a CTkTextbox."""

    def __init__(self, textbox: ctk.CTkTextbox):
        self._box = textbox

    def write(self, text: str):
        self._box.configure(state="normal")
        self._box.insert("end", text)
        self._box.see("end")
        self._box.configure(state="disabled")

    def flush(self):
        pass


class ScrollableConsoleFrame(ctk.CTkFrame):
    """A read-only console log panel that captures stdout and stderr."""

    def __init__(self, master=None, **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Header label
        ctk.CTkLabel(
            self,
            text="Console",
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, padx=PAD_OUTER, pady=(6, 0), sticky="w")

        # Monospace textbox for log output
        self._textbox = ctk.CTkTextbox(
            self,
            state="disabled",
            font=ctk.CTkFont(family="Courier New", size=11),
            wrap="word",
            activate_scrollbars=True,
        )
        self._textbox.grid(
            row=1, column=0, padx=PAD_OUTER, pady=(2, 2), sticky="nsew"
        )
        self.grid_rowconfigure(1, weight=1)

        # Clear button
        ctk.CTkButton(
            self,
            text="Clear",
            width=60,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            command=self._clear,
        ).grid(row=2, column=0, padx=PAD_OUTER, pady=(0, 6), sticky="e")

        # Redirect stdout / stderr
        redirector = RedirectText(self._textbox)
        sys.stdout = redirector
        sys.stderr = redirector

        # Custom exception handlers
        sys.excepthook = self._handle_exception
        self.master.report_callback_exception = self._handle_tk_exception

    def _clear(self):
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.configure(state="disabled")

    def _handle_exception(self, exc_type, exc_value, exc_tb):
        if issubclass(exc_type, AssertionError):
            sys.stderr.write(str(exc_value) + "\n")
        else:
            import traceback
            sys.stderr.write(
                "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            )

    def _handle_tk_exception(self, exc_type, exc_value, exc_tb):
        if issubclass(exc_type, AssertionError):
            sys.stderr.write("Warning: " + str(exc_value) + "\n")
        else:
            import traceback
            sys.stderr.write(
                "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            )

# ----------------------------------------------------------------------
