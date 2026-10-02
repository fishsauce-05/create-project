import sys
from ..creator import CreateProject
from ..helper import DirectoryManager, FileWriter, TextReplacer
from abc import ABC, abstractmethod
from typing import override
from pathlib import Path

class CreateProjectByTemplate(CreateProject, ABC):
    def __init__(self):
        super().__init__()
        self.text = TextReplacer()
        self.file = FileWriter()
        self.dirs = DirectoryManager()

    @property
    def template_path(self) -> Path:
        if getattr(sys, "frozen", False):
            base_dir = Path(sys._MEIPASS)
        else:
            base_dir = Path(__file__).resolve().parents[3]
        return base_dir / "boilerplate"
    
    @property
    @abstractmethod
    def renamed_dir(self) -> dict[str, str]:
        pass
    
    @property
    @abstractmethod
    def replaced_text(self) -> dict[str, str]:
        pass
    
    @property
    @abstractmethod
    def ignored_patterns(self) -> list[str]:
        pass

    @property
    def new_files(self) -> dict[Path, str]:
        return None
        
    @override
    def _do_execute(self):
        project_dir = self.__copy_template()
        self.dirs.rename_directories(
            project_dir = project_dir,
            renamed_dirs = self.renamed_dir
        )
        self.text.replace(project_dir, self.replaced_text, self.ignored_patterns)
        if self.new_files:
            self.file.insert_many(self.new_files)
        
    def __copy_template(self):
        project_name = self.user_input.get("project_name", "")
        project_dir = self.project_path / project_name
        return self.dirs.copy_template(
            src = self.template_path,
            dst = project_dir
        )