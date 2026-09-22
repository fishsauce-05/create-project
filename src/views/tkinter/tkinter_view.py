import tkinter as tk
from views.base.view import View
from views.tkinter.tkinter_input import TkinterInput
from typing import override

class TkinterView(View):
    def __init__(self):
        self.root = tk.Tk()
        self.input = TkinterInput(self.root)
        self.root.title("Create Project")
        self.root.geometry("400x300")
        self.row = 0
        self.form_frame = None
        
    @override
    def select_project_type(self, project_types, on_select):
        result = self.input.dropdown_input(self.row, project_types, on_select)
        self.row += 1
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
        tk.messagebox.showerror("Error", message)  
        
    @override
    def render_form(self, requirements, on_submit):
        if self.form_frame is not None:
            self.form_frame.destroy()
            
        self.form_frame = tk.Frame(self.root)
        self.form_frame.grid(row=self.row, column=0, columnspan=2, sticky="ew")
        
        fields = {}
        for key, value in requirements.items():
            if value['type'] == 'str':
                fields[key] = self.input.str_input(self.row, value, self.form_frame)
            elif value['type'] == 'radio':
                fields[key] = self.input.radio_input(self.row, value, self.form_frame)
            self.row += 1
            
        def submit():
            user_input = {
                key: field.value()
                for key, field in fields.items()
            }

            missing = [
                requirements[key]["name"]
                for key, value in user_input.items()
                if requirements[key].get("required") and not value
            ]
            if missing:
                self.show_error(f"Required field: {', '.join(missing)}")
                return

            on_submit(user_input)

        submit_button = tk.Button(
                            self.form_frame, 
                            text="Submit", 
                            command=submit
                        )
        submit_button.grid(row=self.row, column=0, columnspan=2)
        self.row += 1
        