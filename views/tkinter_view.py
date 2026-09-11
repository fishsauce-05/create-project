from views.view import View
from typing import override
import tkinter as tk
from tkinter import messagebox

class TkinterView(View):
    def __init__(self):
        self.root = tk.Tk()
        self.lastRow = 0
        self.result = {}
        self._on_submit = None
        self._dynamic_frame = None

    def __dropdown_input(self, labelText, default_value, options):
        label = tk.Label(self.root, text=labelText)
        label.grid(row=self.lastRow, column=0, sticky="w")

        variable = tk.StringVar(value=default_value)

        dropdown = tk.OptionMenu(self.root, variable, *options)
        dropdown.grid(row=self.lastRow, column=1, sticky="ew")

        self.lastRow += 1

        return variable

    def __str_input(self, parent, labelText):
        label = tk.Label(parent, text=labelText)
        label.grid(row=self.lastRow, column=0, sticky="w")

        entry = tk.Entry(parent)
        entry.grid(row=self.lastRow, column=1, sticky="ew")

        self.lastRow += 1

        return entry

    def __radio_input(self, parent, req):
        label = tk.Label(parent, text=req["prompt"])
        label.grid(row=self.lastRow, column=0, sticky="w")

        variable = tk.StringVar(value=req["option"][0])

        curColumn = 1
        for option in req["option"]:
            radio = tk.Radiobutton(parent, text=option, variable=variable, value=option)
            radio.grid(row=self.lastRow, column=curColumn, sticky="w")
            curColumn += 1

        self.lastRow += 1

        return variable

    def __submit(self, entries):
        result = {
            key: value.get()
            for key, value in entries.items()
        }
        if any(not value.strip() for value in result.values()):
            messagebox.showerror("Invalid input", "Please fill in all required fields.")
            return

        self.result = result
        self._on_submit(result)

    @override
    def activateUI(self):
        self.root.title("Project Creator")
        self.root.geometry("400x300")
        self.root.columnconfigure(1, weight=1)

    @override
    def select_project_type(self, project_type, on_select):
        variable = self.__dropdown_input(
            "Select Project Type:",
            "---Select option---",
            project_type
        )
        variable.trace_add(
            "write",
            lambda *args: on_select(variable.get())
                if (variable.get() != "---Select option---") else None
        )

    @override
    def select_project_input(self, requirements, on_submit):
        self._on_submit = on_submit

        if self._dynamic_frame is not None:
            self._dynamic_frame.destroy()

        self._dynamic_frame = tk.Frame(self.root)
        self._dynamic_frame.grid(row=self.lastRow, column=0, columnspan=2, sticky="ew")
        self._dynamic_frame.columnconfigure(1, weight=1)

        entries = {}
        dynamicRow = 0

        for requirement, req in requirements.items():
            match req["type"]:
                case "str":
                    entries[requirement] = self.__str_input(self._dynamic_frame, req["prompt"])
                case "radio":
                    entries[requirement] = self.__radio_input(self._dynamic_frame, req)
                case _:
                    raise ValueError(f"Unsupported requirement type: {req}")

        button = tk.Button(
            self._dynamic_frame,
            text="Submit",
            command=lambda: self.__submit(entries)
        )
        button.grid(
            row=self.lastRow,
            column=0,
            columnspan=2,
            pady=10
        )

    @override
    def run(self):
        self.root.mainloop()

    @override
    def close(self):
        self.root.destroy()

    @override
    def show_error(self, message):
        messagebox.showerror("Command failed", message)
