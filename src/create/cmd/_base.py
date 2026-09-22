from ..creator import CreateProject
from abc import ABC, abstractmethod
from typing import override
import subprocess
import shlex

class CreateProjectByCommand(CreateProject, ABC):
    def __init__(self):
        super().__init__()
        
    @override
    def _do_execute(self) -> None:
        results = self.command.split('&&')
        cwd = self.project_path
        for result in results:
            parts = shlex.split(result.strip())
            if parts and parts[0] == "cd":
                cwd = cwd / parts[1]
                continue
            subprocess.run(
                parts,
                cwd=str(cwd),
                shell=True,
                check=True
            )

    @property
    @abstractmethod
    def command(self) -> str:
        pass