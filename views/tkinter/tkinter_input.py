import tkinter as tk
from tkinter import messagebox
from typing import Callable
from typing import override
from views.base.field import Field
from views.base.ui_input import UIInput

class TkinterInput(UIInput):

    def __init__(self, root: tk.Misc):
        self._root = root
        
    @override
    def dropdown_input(self, row: int, options: list[str], on_select: Callable[[str], None]):
        PROJECT_TYPE_LABEL = "Select project type:"
        DROPDOWN_PLACEHOLDER = "---Select an option---"
        label = tk.Label(self._root, text=PROJECT_TYPE_LABEL)
        label.grid(row=row, column=0, sticky="w")
        variable = tk.StringVar(value=DROPDOWN_PLACEHOLDER)
        
        menu = tk.OptionMenu(self._root, variable, *options)
        menu.grid(row=row, column=1, sticky="ew")
        
        variable.trace_add(
            "write",
            lambda *args: on_select(variable.get())
        )
        return Field(variable.get)
        
    @override
    def str_input(self, row: int, req: dict, parent: tk.Misc = None):
        default = req.get("default")
        
        label = tk.Label(parent, text=req["prompt"])
        label.grid(row=row, column=0, sticky="w")
        entry = tk.Entry(parent)
        entry.grid(row=row, column=1, sticky="ew")
        
        if default is not None:
            entry.insert(0, default)
        return Field(entry.get, default=default)

    @override
    def radio_input(self, row: int, req: dict, parent: tk.Misc = None):
        label = tk.Label(parent, text=req["prompt"])
        label.grid(row=row, column=0, sticky="w")
        
        variable = tk.StringVar(value=req["option"][0])
        for i, option in enumerate(req["option"], start=1):
            radio = tk.Radiobutton(parent, text=option, variable=variable, value=option)
            radio.grid(row=row, column=i, sticky="w")
        return Field(variable.get, default = req["option"][0])