import tkinter as tk
from typing import override
from views.base.field import Field
from views.base import specification as specs
from views.base.ui_input import UIInput

class TkinterInput(UIInput):
    def __init__(self, root: tk.Misc):
        self._root = root
        self._parent: tk.Misc = root
        self._row = 0

    def set_container(self, parent: tk.Misc, start_row: int = 0) -> None:
        self._parent = parent
        self._row = start_row

    @property
    def row(self) -> int:
        return self._row

    @override
    def dropdown_input(self, spec: specs.DropdownSpec) -> Field:
        label = tk.Label(self._parent, text=spec.prompt)
        label.grid(row=self._row, column=0, sticky="w")

        variable = tk.StringVar(value=spec.placeholder)
        menu = tk.OptionMenu(self._parent, variable, *spec.options)
        menu.grid(row=self._row, column=1, sticky="ew")

        callback = spec.on_select
        if callback is not None:
            def on_write(*_args):
                value = variable.get()
                if value != spec.placeholder:
                    callback(value)

            variable.trace_add("write", on_write)
        self._row += 1
        return Field(variable.get)

    @override
    def str_input(self, spec: specs.StrSpec) -> Field:
        label = tk.Label(self._parent, text=spec.prompt)
        label.grid(row=self._row, column=0, sticky="w")

        entry = tk.Entry(self._parent)
        entry.grid(row=self._row, column=1, sticky="ew")

        if spec.default is not None:
            entry.insert(0, spec.default)
        self._row += 1
        return Field(entry.get, default=spec.default)

    @override
    def radio_input(self, spec: specs.RadioSpec) -> Field:
        options = list(spec.options)
        default = spec.default if spec.default is not None else (options[0] if options else "")

        label = tk.Label(self._parent, text=spec.prompt)
        label.grid(row=self._row, column=0, sticky="w")

        variable = tk.StringVar(value=default)
        for i, option in enumerate(options, start=1):
            radio = tk.Radiobutton(self._parent, text=option, variable=variable, value=option)
            radio.grid(row=self._row, column=i, sticky="w")
        self._row += 1
        return Field(variable.get, default=default)

    @override
    def checkbox_input(self, spec: specs.CheckboxSpec) -> Field:
        label = tk.Label(self._parent, text=spec.prompt)
        label.grid(row=self._row, column=0, sticky="w")

        variable = tk.BooleanVar(value=spec.default)
        check = tk.Checkbutton(self._parent, variable=variable)
        check.grid(row=self._row, column=1, sticky="w")
        self._row += 1
        return Field(variable.get, default=spec.default)