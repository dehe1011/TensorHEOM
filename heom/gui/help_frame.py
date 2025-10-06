import os
import customtkinter as ctk
from PIL import Image, ImageTk

from ..import ROOT_DIR

# ----------------------------------------------------------------------


class HelpFrame(ctk.CTkFrame):
    def __init__(self, master):

        # initialization of the ctk.CTkFrame class
        super().__init__(master)
        row = 0

        # label
        self.logo_label = ctk.CTkLabel(
            self, text="Help", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=row, column=0, pady=10, padx=10)
        row += 1

        # Load image with PIL
        img = Image.open(os.path.join(ROOT_DIR,"docs", "figures", "entangling_qc.png"))
        ctk_img = ctk.CTkImage(light_image=img, size=(100, 100/1.3))

        # Use in CTkLabel
        label = ctk.CTkLabel(self, image=ctk_img, text="")
        label.grid(row=row, column=0, pady=10, padx=10)
        row += 1

        # github link
        self.github_button = ctk.CTkButton(
            self, text="GitHub", command=master.open_github
        )
        self.github_button.grid(row=row, column=0, pady=10, padx=10)
        row += 1

        # paper link
        self.paper_button = ctk.CTkButton(
            self, text="Paper", command=master.open_paper
        )
        self.paper_button.grid(row=row, column=0, pady=10, padx=10)
        row += 1

        # help button 
        self.manual_button = ctk.CTkButton(
            self, text="Help", command=master.open_help_window
        )
        self.manual_button.grid(row=row, column=0, pady=10, padx=10)
        row += 1


# ----------------------------------------------------------------------