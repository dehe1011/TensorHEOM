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
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        row = 0

        # Logo
        try:
            img = Image.open(
                os.path.join(ROOT_DIR, "ttheom", "figures", "logo.png")
            )
            width = 80
            height = int(width * img.height / img.width)
            ctk_img = ctk.CTkImage(light_image=img, size=(width, height))
            ctk.CTkLabel(self, image=ctk_img, text="").grid(
                row=row, column=0, columnspan=3, pady=(PAD_OUTER, 2)
            )
        except Exception:
            pass
        row += 1

        # Three equal-width buttons in a row
        ctk.CTkButton(
            self,
            text="GitHub",
            width=BTN_WIDTH_SECONDARY,
            height=28,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            font=ctk.CTkFont(size=11),
            command=master.open_github,
        ).grid(row=row, column=0, padx=(PAD_OUTER, 2), pady=(2, PAD_OUTER), sticky="ew")

        ctk.CTkButton(
            self,
            text="Paper",
            width=BTN_WIDTH_SECONDARY,
            height=28,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            font=ctk.CTkFont(size=11),
            command=master.open_paper,
        ).grid(row=row, column=1, padx=2, pady=(2, PAD_OUTER), sticky="ew")

        ctk.CTkButton(
            self,
            text="Help",
            width=BTN_WIDTH_SECONDARY,
            height=28,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            font=ctk.CTkFont(size=11),
            command=master.open_help_window,
        ).grid(row=row, column=2, padx=(2, PAD_OUTER), pady=(2, PAD_OUTER), sticky="ew")

# ----------------------------------------------------------------------
