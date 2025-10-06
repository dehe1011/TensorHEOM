import customtkinter as ctk

# ----------------------------------------------------------------------

class HelpWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Help")
        self.geometry("500x400")

        # Configure grid for resizing
        self.grid_rowconfigure(1, weight=1)     # row with textbox expands
        self.grid_columnconfigure(0, weight=1)  # column expands

        # Info label
        label = ctk.CTkLabel(self, text="Help and Manual",
                             font=ctk.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=0, pady=10, padx=10, sticky="n")

        # Textbox with scrollable help text
        self.textbox = ctk.CTkTextbox(self, width=480, height=320)
        self.textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Insert your manual/help text
        help_text = (
            "Welcome to the Application Help!\n\n"
            "Here are some instructions:\n"
            "1. ...\n"
            "2. ...\n"
            "3. ...\n\n"
            "For further details, consult the user manual or documentation."
        )
        self.textbox.insert("1.0", help_text)
        self.textbox.configure(state="disabled")  # make read-only


# ----------------------------------------------------------------------
