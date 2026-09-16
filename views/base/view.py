from abc import ABC, abstractmethod
from typing import Callable

class View(ABC):    
    @abstractmethod
    def select_project_type(self, project_type: str, on_select: Callable[[str], None]):
        pass
    
    @abstractmethod
    def select_project_input(self, requirements: dict, on_submit: Callable[[dict], None]):
        pass
    
    @abstractmethod
    def run(self):
        pass
    
    @abstractmethod
    def close(self):
        pass
    
    @abstractmethod
    def show_error(self, message: str):
        pass    
    
    @abstractmethod
    def render_form(self, requirements: dict, on_submit: Callable[[dict], None]):
        pass