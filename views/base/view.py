from abc import ABC, abstractmethod
from typing import Callable

class View(ABC):    
    @abstractmethod
    def select_project_type(self, project_type: str, on_select: Callable[[str], None]) -> None:
        pass
    
    @abstractmethod
    def select_project_input(self, requirements: dict[str, dict[str, str]], on_submit: Callable[[dict], None]) -> None:
        pass
    
    @abstractmethod
    def run(self) -> None:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass
    
    @abstractmethod
    def show_error(self, message: str) -> None:
        pass    
    
    @abstractmethod
    def render_form(self, requirements: dict[str, dict[str, str]], on_submit: Callable[[dict], None]) -> None:
        pass