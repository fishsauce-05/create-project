from abc import ABC, abstractmethod
from typing import Callable

class UIInput(ABC):
    @abstractmethod
    def dropdown_input(self, options: list[str], on_select: Callable[[str], None]):
        pass
    
    @abstractmethod
    def str_input(self, row: int, req: dict):
        pass
    
    @abstractmethod
    def radio_input(self, label: str, options: list[str]):
        pass