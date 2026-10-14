from views.base.view import View
from create.registry import Registry
from concurrency.runner import BackgroundRunner

class ProjectController:
    def __init__(self, view: View, registry: Registry, runner: BackgroundRunner):
        self.view = view
        self.registry = registry
        self.runner = runner

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
            lambda user_input: self._execute(creator, user_input)
        )

    def _execute(self, creator, user_input):
        creator.user_input = user_input
        self.view.show_progress("Creating project…")
        self.runner.run(
            work = creator.execute,
            on_success = self._on_success,
            on_error = self._on_error
        )

    def _on_success(self):
        self.view.close_progress()
        self.view.close()

    def _on_error(self, message):
        self.view.close_progress()
        self.view.show_error(message)