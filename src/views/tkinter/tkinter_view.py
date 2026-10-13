import tkinter as tk
import views.base.specification as specs
from tkinter import messagebox
from typing import override
from views.base.field import Field
from views.base.view import View
from views.tkinter.tkinter_input import TkinterInput

class TkinterView(View):
    def __init__(self):
        self.root = tk.Tk()
        self.input = TkinterInput(self.root)
        self.root.title("Create Project")
        self.root.geometry("500x400")
        self.row = 0
        self.form_frame = None

    @override
    def select_project_type(self, project_types, on_select):
        self.input.set_container(self.root, self.row)
        result = self.input.dropdown_input(
            specs.DropdownSpec(
                prompt="Select project type:",
                options=list(project_types),
                on_select=on_select,
            )
        )
        self.row = self.input.row
        return result

    @override
    def select_project_input(self, requirements, on_submit):
        self.render_form(requirements, on_submit)

    @override
    def run(self):
        self.root.mainloop()

    @override
    def close(self):
        self.root.destroy()

    @override
    def show_error(self, message):
        messagebox.showerror("Error", message)

    @override
    def render_form(self, requirements, on_submit):
        if self.form_frame is not None:
            self.form_frame.destroy()

        self.form_frame = tk.Frame(self.root)
        self.form_frame.grid(row=self.row, column=0, columnspan=2, sticky="ew")
        self.row += 1

        self.input.set_container(self.form_frame, 0)

        fields = {}
        for key, req in requirements.items():
            fields[key] = self._build_field(req)

        submit_button = tk.Button(
            self.form_frame,
            text="Submit",
            command=lambda: self._submit(fields, requirements, on_submit),
        )
        submit_button.grid(row=self.input.row, column=0, columnspan=2)

    def _build_field(self, req: dict) -> Field:
        match req["type"]:
            case "str":
                return self.input.str_input(
                    specs.StrSpec(prompt=req["prompt"], default=req.get("default"))
                )
            case "radio":
                options = list(req["option"])
                default = req.get("default") or (options[0] if options else None)
                return self.input.radio_input(
                    specs.RadioSpec(prompt=req["prompt"], options=options, default=default)
                )
            case "checkbox":
                return self.input.checkbox_input(
                    specs.CheckboxSpec(prompt=req["prompt"], default=req.get("default", False))
                )
            case _:
                raise ValueError(f"Unsupported input type: {req['type']}")

    def _submit(self, fields, requirements, on_submit):
        user_input = {
            key: field.value()
            for key, field in fields.items()
        }

        missing = [
            requirements[key].get("name", key)
            for key, field in fields.items()
            if requirements[key].get("required")
            and requirements[key]["type"] != "checkbox"
            and not field.value()
        ]
        if missing:
            self.show_error(f"Required field: {', '.join(missing)}")
            return

        on_submit(user_input)
