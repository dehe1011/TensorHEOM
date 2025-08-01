import os

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ----------------------------------------------------------------------

class PlottingFrame(ctk.CTkFrame):
    def __init__(self, master):

        # initialization of the ctk.CTkFrame class
        super().__init__(master)

        # widgets
        self.filename_label = ctk.CTkLabel(self, text="Filename:")
        self.filename_label.grid(row=0, column=0, pady=10, padx=10)

        self.filename_entry = ctk.CTkEntry(self)
        self.filename_entry.grid(row=1, column=0, padx=10, pady=10)

        self.directory_label = ctk.CTkLabel(self, text="Directory:")
        self.directory_label.grid(row=0, column=1, pady=10, padx=10)

        self.directory_entry = ctk.CTkEntry(self)
        self.directory_entry.grid(row=1, column=1, padx=10, pady=10)

        self.subframe = ctk.CTkFrame(self)
        self.subframe.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.save_button = ctk.CTkButton(self, text="Save", command=master.save)
        self.save_button.grid(row=4, column=0, padx=10, pady=10)

        self.cancel_button = ctk.CTkButton(self, text="Cancel", command=master.cancel)
        self.cancel_button.grid(row=4, column=1, padx=10, pady=10)

class PlottingWindow(ctk.CTkToplevel):
    def __init__(self, master):

        # initialization of the ctk.CTkToplevel class
        super().__init__(master)
        self.title("Plotting")
        self.controller = master

        self.plotting_frame = PlottingFrame(self)
        self.plotting_frame.grid(
            row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"
        )

        if self.controller.plot_kwargs['plot_type'] == 'Full density matrix':
            self.plot_dm()

        self.plotting(self.fig)

    # ------------------------------------------------------------------

    def plot_dm(self):
        self.fig, self.ax = plt.subplots(4,4, figsize=(2*3.4, 2*2.1), sharex=True, sharey=True)
        for i, a in enumerate(self.ax.flatten()):
            a.plot(self.controller.result[0], self.controller.result[i+1].values.real)
            a.plot(self.controller.result[0], self.controller.result[i+1].values.imag)

            a.set_yticks([-1, -0.5, 0, 0.5, 1])

    # ------------------------------------------------------------------

    def save(self):
        filename = self.plotting_frame.filename_entry.get()
        directory = self.plotting_frame.directory_entry.get()
        filepath = os.path.join(directory, filename)
        self.fig.savefig(filepath)
        self.destroy()

    def cancel(self):
        self.destroy()

    def plotting(self, fig):
        for widget in self.plotting_frame.subframe.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.plotting_frame.subframe)
        canvas.draw()
        canvas.get_tk_widget().pack()


# ----------------------------------------------------------------------