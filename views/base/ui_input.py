from abc import ABC, abstractmethod
from typing import Callable

from views.base.field import Field

class UIInput(ABC):
    @abstractmethod
    def dropdown_input(self, options: list[str], on_select: Callable[[str], None]) -> Field:
        pass
    
    @abstractmethod
    def str_input(self, row: int, req: dict[str, str]) -> Field:
        pass
    
    @abstractmethod
    def radio_input(self, label: str, options: list[str]) -> Field:
        pass