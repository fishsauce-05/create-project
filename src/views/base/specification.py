from dataclasses import dataclass
from typing import Callable, Sequence

@dataclass(frozen=True)
class DefaultSpec:
	prompt: str

@dataclass(frozen=True)
class StrSpec(DefaultSpec):
	default: str | None = None

@dataclass(frozen=True)
class RadioSpec(DefaultSpec):
	options: Sequence[str] = ()
	default: str | None = None

@dataclass(frozen=True)
class DropdownSpec(DefaultSpec):
	options: Sequence[str] = ()
	on_select: Callable[[str], None] | None = None
	placeholder: str = "---Select an option---"

@dataclass(frozen=True)
class CheckboxSpec(DefaultSpec):
	default: bool = False