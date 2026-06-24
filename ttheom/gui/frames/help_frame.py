import os
import customtkinter as ctk
from PIL import Image

from ...import ROOT_DIR
from ..gui_utils import PAD_OUTER, PAD_Y, BTN_WIDTH_SECONDARY

# ----------------------------------------------------------------------


class HelpFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=10)

        self.grid_columnconfigure(0, weight=1)

        row = 0

        # Logo
        try:
            img = Image.open(
                os.path.join(ROOT_DIR, "ttheom", "figures", "logo.png")
            )
            width = 120
            height = int(width * img.height / img.width)
            ctk_img = ctk.CTkImage(light_image=img, size=(width, height))

            ctk.CTkLabel(self, image=ctk_img, text="").grid(
                row=row,
                column=0,
                padx=PAD_OUTER,
                pady=(PAD_OUTER, 4),
                sticky="ew",
            )
        except Exception:
            pass

        row += 1

        # # ── spacer ───────────────────────────────────────────────────────
        # self.grid_rowconfigure(row, weight=1)
        # row += 1

        # Three buttons in three rows
        buttons = [
            ("GitHub", master.open_github),
            ("Paper", master.open_paper),
            ("Help", master.open_help_window),
        ]

        for text, command in buttons:
            ctk.CTkButton(
                self,
                text=text,
                width=BTN_WIDTH_SECONDARY,
                height=28,
                fg_color=("gray65", "gray25"),
                hover_color=("gray55", "gray35"),
                # font=ctk.CTkFont(size=11),
                command=command,
            ).grid(
                row=row,
                column=0,
                padx=PAD_OUTER,
                pady=2,
                sticky="ew",
            )
            row += 1

# ----------------------------------------------------------------------
