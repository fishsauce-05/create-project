from abc import ABC, abstractmethod
from views.base.field import Field
from views.base import specification as specs

class UIInput(ABC):
    @abstractmethod
    def str_input(self, spec: specs.StrSpec) -> Field:
        pass
    
    @abstractmethod
    def radio_input(self, spec: specs.RadioSpec) -> Field:
        pass

    @abstractmethod
    def checkbox_input(self, spec: specs.CheckboxSpec) -> Field:
        pass

    @abstractmethod
    def dropdown_input(self, spec: specs.DropdownSpec) -> Field:
        pass

    def create_input(self, requirements: dict[str, dict[str, str]]) -> Field:
        match requirements["type"]:
            case "str":
                return self.str_input(specs.StrSpec(requirements["prompt"]), requirements.get("default"))
            case "radio":
                return self.radio_input(specs.RadioSpec(requirements["prompt"]), requirements["option"], requirements.get("default"))
            case "checkbox":
                return self.checkbox_input(specs.CheckboxSpec(requirements["prompt"]))
            case "dropdown":
                return self.dropdown_input(specs.DropdownSpec(requirements["prompt"], requirements["option"]))
            case _:
                raise ValueError("Unsupported type")