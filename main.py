from commands.cmd import Cmd
from views.tkinter_view import TkinterView
from views.view import View
from registry import Registry

class Main:
    def __init__(self, view: View, registry: Registry):
        self.view = view
        self.registry = registry

    def run(self):
        self.view.activateUI()
        self.view.select_project_type(
            self.registry.get_project_types(),
            self._select_project_type
        )
        self.view.run()

    def _select_project_type(self, project_type):
        cmd = self.registry.create(project_type)
        self.view.select_project_input(
            cmd.requirements,
            lambda user_input: self._execute_command(cmd, user_input)
        )

    def _execute_command(self, cmd, user_input):
            print("USER INPUT:", user_input)
            cmd.user_input = user_input
            try:
                cmd.execute()
            except Exception as e:
                error_msg = str(e)
                self.view.root.after(
                    0,
                    lambda: self.view.show_error(error_msg)
                )
                return
            self.view.close()


if __name__ == "__main__":
    Main(TkinterView(), Registry()).run()