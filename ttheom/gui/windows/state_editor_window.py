import sys
import io
from tkinter import messagebox

import customtkinter as ctk

from ..gui_utils import PAD_OUTER


class StateEditor(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Initial State Editor")
        self.geometry("460x430")
        self.minsize(420, 380)
        self.master = master

        # Track whether the state was successfully confirmed
        self.state_confirmed = False
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)  # code editor
        self.grid_rowconfigure(4, weight=1)  # console

        # ── instruction ──────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text=(
                f"Define the initial density matrix for {master.numQ} qubit(s).\n"
                "The variable must be named  init_state."
            ),
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w",
        ).grid(
            row=0,
            column=0,
            padx=PAD_OUTER,
            pady=(PAD_OUTER, 6),
            sticky="w",
        )

        # ── code editor ──────────────────────────────────────────────────
        self.code_box = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Courier New", size=12),
            wrap="none",
            height=160,
        )
        self.code_box.grid(
            row=1,
            column=0,
            padx=PAD_OUTER,
            pady=(0, 8),
            sticky="nsew",
        )

        self.code_box.insert("1.0", "import numpy as np\n\n")
        self.code_box.insert(
            "end",
            f"init_state = {self.master.kwargs['rhoIni'].tolist()}\n",
        )

        # ── confirm button ───────────────────────────────────────────────
        ctk.CTkButton(
            self,
            text="Confirm Initial State",
            width=180,
            height=30,
            command=self._confirm,
        ).grid(row=2, column=0, pady=(0, 8))

        # ── console label ────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="Console",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).grid(
            row=3,
            column=0,
            padx=PAD_OUTER,
            pady=(0, 2),
            sticky="w",
        )

        # ── console / output box ─────────────────────────────────────────
        self.output_box = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Courier New", size=11),
            state="disabled",
            height=90,
            wrap="word",
        )
        self.output_box.grid(
            row=4,
            column=0,
            padx=PAD_OUTER,
            pady=(0, PAD_OUTER),
            sticky="nsew",
        )

    # ------------------------------------------------------------------

    def _confirm(self):
        user_code = self.code_box.get("1.0", "end-1c")

        old_out, old_err = sys.stdout, sys.stderr
        buf_out, buf_err = io.StringIO(), io.StringIO()
        sys.stdout, sys.stderr = buf_out, buf_err

        try:
            local_env = {}
            exec(user_code, {}, local_env)  # nosec

            if "init_state" not in local_env:
                raise ValueError("No variable named `init_state` was defined.")

            self.master.kwargs["rhoIni"] = local_env["init_state"]
            self.state_confirmed = True

            stdout_text = buf_out.getvalue().strip()
            stderr_text = buf_err.getvalue().strip()

            msg = "✓ Initial state set successfully."
            if stdout_text:
                msg += f"\n\nstdout:\n{stdout_text}"
            if stderr_text:
                msg += f"\n\nstderr:\n{stderr_text}"

            self._set_console(msg)

        except Exception as exc:
            stdout_text = buf_out.getvalue().strip()
            stderr_text = buf_err.getvalue().strip()

            msg = f"✗ Error:\n{exc}"
            if stdout_text:
                msg += f"\n\nstdout:\n{stdout_text}"
            if stderr_text:
                msg += f"\n\nstderr:\n{stderr_text}"

            self._set_console(msg)

        finally:
            sys.stdout, sys.stderr = old_out, old_err

    def _set_console(self, msg: str):
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.insert("end", msg)
        self.output_box.configure(state="disabled")

    def _on_close(self):
        if not self.state_confirmed:
            proceed = messagebox.askyesno(
                "Initial state not confirmed",
                "You have not confirmed the initial state yet.\n\n"
                "Do you really want to close the editor?",
                parent=self,
            )
            if not proceed:
                return

        self.destroy()