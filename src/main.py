from views.base.view import View
from views.tkinter.tkinter_view import TkinterView
from create.registry import Registry

class Main:
    def __init__(self, view: View, registry: Registry):
        self.view = view
        self.registry = registry

    def run(self):
        self.view.select_project_type(
            self.registry.get_project_types(),
            self._select_project_type
        )
        self.view.run()

    def _select_project_type(self, project_type):
        creator = self.registry.create(project_type)
        self.view.select_project_input(
            creator.requirements,
            lambda user_input: self._execute_command(creator, user_input)
        )

    def _execute_command(self, creator, user_input):
            print("USER INPUT:", user_input)
            creator.user_input = user_input
            try:
                creator.execute()
            except Exception as e:
                self.view.show_error(str(e))
                return
            self.view.close()

if __name__ == "__main__":
    Main(TkinterView(), Registry()).run()