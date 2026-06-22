import customtkinter as ctk

# ----------------------------------------------------------------------


def change_state_all_widgets(frame, state):
    for widget in frame.winfo_children():
        if isinstance(
            widget, ctk.CTkBaseClass
        ):  # Check if the widget is a customtkinter widget
            widget.configure(state=state)
        elif isinstance(
            widget, ctk.CTkFrame
        ):  # Recursively disable widgets in nested frames
            change_state_all_widgets(widget, state)

class Counter(ctk.CTkFrame):
    def __init__(self, master=None, start=1, minimum=1, maximum=3):
        super().__init__(master)
        self.value = start
        self.min_val = minimum
        self.max_val = maximum

        self.decrease_btn = ctk.CTkButton(self, text="-", width=40, command=self.decrease)
        self.decrease_btn.pack(side="left", padx=5)

        self.label = ctk.CTkLabel(self, text=str(self.value), width=40)
        self.label.pack(side="left", padx=5)

        self.increase_btn = ctk.CTkButton(self, text="+", width=40, command=self.increase)
        self.increase_btn.pack(side="left", padx=5)

    def increase(self):
        if self.value < self.max_val:
            self.value += 1
            self.label.configure(text=str(self.value))

    def decrease(self):
        if self.value > self.min_val:
            self.value -= 1
            self.label.configure(text=str(self.value))

    def get(self):
        return self.value

    def configure(self, state):
        """Enable/disable the counter"""
        self.increase_btn.configure(state=state)
        self.decrease_btn.configure(state=state)

# ----------------------------------------------------------------------
