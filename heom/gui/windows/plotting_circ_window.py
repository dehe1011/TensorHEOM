import os

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ----------------------------------------------------------------------

class PlottingCircFrame(ctk.CTkFrame):
    def __init__(self, master):

        # initialization of the ctk.CTkFrame class
        super().__init__(master)
        self.master = master

        # filename label and entry
        self.filename_label = ctk.CTkLabel(self, text="Filename:")
        self.filename_label.grid(row=0, column=0, pady=10, padx=10)

        self.filename_entry = ctk.CTkEntry(self)
        self.filename_entry.grid(row=1, column=0, padx=10, pady=10)

        # directory label and entry
        self.directory_label = ctk.CTkLabel(self, text="Directory:")
        self.directory_label.grid(row=0, column=1, pady=10, padx=10)

        self.directory_entry = ctk.CTkEntry(self)
        self.directory_entry.grid(row=1, column=1, padx=10, pady=10)

        # subframe for plotting
        self.subframe = ctk.CTkFrame(self)
        self.subframe.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # save and cancel buttons
        self.save_button = ctk.CTkButton(self, text="Save", command=master.save)
        self.save_button.grid(row=4, column=0, padx=10, pady=10)

        self.cancel_button = ctk.CTkButton(self, text="Cancel", command=master.cancel)
        self.cancel_button.grid(row=4, column=1, padx=10, pady=10)

class PlottingCircWindow(ctk.CTkToplevel):
    def __init__(self, master):

        # initialization of the ctk.CTkToplevel class
        super().__init__(master)
        self.title("Quantum Circuit")
        self.master = master

        self.plotting_frame = PlottingCircFrame(self)
        self.plotting_frame.grid(
            row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"
        )

        self.fig = self.master.qc.draw(output='mpl')

        # display plot in self.plotting_frame.subframe
        for widget in self.plotting_frame.subframe.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(self.fig, master=self.plotting_frame.subframe)
        canvas.draw()
        canvas.get_tk_widget().pack()

    # ------------------------------------------------------------------

    def save(self):
        filename = self.plotting_frame.filename_entry.get()
        directory = self.plotting_frame.directory_entry.get()
        filepath = os.path.join(directory, filename)
        self.fig.savefig(filepath)
        self.destroy()

    def cancel(self):
        self.destroy()

# ----------------------------------------------------------------------