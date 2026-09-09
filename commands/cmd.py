from abc import ABC, abstractmethod
import sys
import subprocess
import shlex
from pathlib import Path
import textwrap

class Cmd(ABC):
    def __init__(self):
        self.project_path = sys.argv[1] if len(sys.argv) > 1 else '.'
        self.user_input = {}
    
    @property
    @abstractmethod
    def requirements(self):
        pass
    
    @property
    @abstractmethod
    def readme(self):
        pass

    @property
    @abstractmethod
    def command(self):
        pass
    
    def __create_guidance(self):
        project_name = self.user_input.get("project_name", "")
        project_dir = Path(self.project_path) / project_name
        guidance = project_dir / "guidance.txt"
        
        cleaned = textwrap.dedent(self.readme).strip()
        guidance.write_text(cleaned, encoding="utf-8")
    
    def execute(self):
        results = self.command.split('&&')
        cwd = Path(self.project_path)
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
        self.__create_guidance()
