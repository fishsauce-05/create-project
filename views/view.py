from abc import ABC, abstractmethod
from typing import Callable

class View(ABC):
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def show_error(self, message):
        pass

    @abstractmethod    
    def activateUI(self):
        pass

    @abstractmethod
    def select_project_type(self, project_type, on_select: Callable[[str], None]):
        pass

    @abstractmethod
    def select_project_input(self, requirements, on_submit: Callable[[dict], None]):
        pass