import sys
import io
import customtkinter as ctk

from ..gui_utils import PAD_OUTER, PAD_Y

# ----------------------------------------------------------------------


class StateEditor(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Initial State Editor")
        self.geometry("480x480")
        self.minsize(400, 400)
        self.master = master
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # ── instruction ──────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text=f"Define the initial density matrix for {master.numQ} qubit(s).\n"
                 "The variable must be named  init_state.",
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w",
        ).grid(row=0, column=0, padx=PAD_OUTER, pady=(PAD_OUTER, 4), sticky="w")

        # ── code editor ──────────────────────────────────────────────────
        self.code_box = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Courier New", size=12),
            wrap="none",
            height=160,
        )
        self.code_box.grid(row=1, column=0, padx=PAD_OUTER, pady=(0, 4), sticky="nsew")
        self.code_box.insert("1.0", "import numpy as np\n\n")
        self.code_box.insert("end", f"init_state = {self.master.kwargs['rhoIni'].tolist()}\n")

        # ── confirm button ────────────────────────────────────────────────
        ctk.CTkButton(
            self, text="Confirm", width=140, command=self._confirm
        ).grid(row=2, column=0, pady=PAD_Y)

        # ── output box ───────────────────────────────────────────────────
        self.output_box = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Courier New", size=11),
            state="disabled",
            height=120,
        )
        self.output_box.grid(row=3, column=0, padx=PAD_OUTER, pady=(0, PAD_OUTER), sticky="nsew")

    # ------------------------------------------------------------------

    def _confirm(self):
        user_code = self.code_box.get("1.0", "end-1c")
        old_out, old_err = sys.stdout, sys.stderr
        buf = io.StringIO()
        sys.stdout = sys.stderr = buf

        try:
            local_env = {}
            exec(user_code, {}, local_env)   # nosec
            self.master.kwargs["rhoIni"] = local_env["init_state"]
            result = "✓ Initial state set.\n" + str(local_env["init_state"])
        except Exception as exc:
            result = f"✗ Error: {exc}"
        finally:
            sys.stdout, sys.stderr = old_out, old_err

        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.insert("end", result)
        self.output_box.configure(state="disabled")

# ----------------------------------------------------------------------
