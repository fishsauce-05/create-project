from controller import ProjectController
from views.tkinter.tkinter_view import TkinterView
from create.registry import Registry
from concurrency.threaded_runner import ThreadedBackgroundRunner

if __name__ == "__main__":
    view = TkinterView()
    registry = Registry()
    runner = ThreadedBackgroundRunner(post=view.post)

    context = ProjectController(view, registry, runner)
    context.run()