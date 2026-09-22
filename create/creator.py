from abc import ABC, abstractmethod
import sys
import textwrap
from pathlib import Path

class CreateProject(ABC):
    def __init__(self):
        self.project_path = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
        self.user_input = {}

    @property
    @abstractmethod
    def requirements(self) -> dict[str, dict[str, str]]:
        pass
    
    @property
    @abstractmethod
    def readme(self) -> str:
        pass

    def execute(self):
        self._validate_requirements()
        self._do_execute()
        self._create_guidance()

    def _validate_requirements(self):
        missing = [key for key in self.requirements if key not in self.user_input and self.requirements[key].get("required", False)]
        if missing:
            raise ValueError(f"Missing required inputs: {', '.join(missing)}")
        
    @abstractmethod
    def _do_execute(self) -> None:
        pass

    def _create_guidance(self):
        project_name = self.user_input.get("project_name", "")
        project_dir = self.project_path / project_name
        guidance = project_dir / "guidance.txt"
        
        cleaned = textwrap.dedent(self.readme).strip()
        guidance.write_text(cleaned, encoding="utf-8")