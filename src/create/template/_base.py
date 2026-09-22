import sys

from ..creator import CreateProject
from ..helper.text_replacer import TextReplacer
from abc import ABC, abstractmethod
from typing import override
from pathlib import Path
import shutil

class CreateProjectByTemplate(CreateProject, ABC):
    def __init__(self):
        super().__init__()
        self.text = TextReplacer()

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
        
    @override
    def _do_execute(self):
        project_dir = self.__copy_template()
        self.__rename_directories(project_dir)
        self.text.replace(project_dir, self.replaced_text, self.ignored_patterns)
        
    def __copy_template(self):
        project_name = self.user_input.get("project_name", "")
        project_dir = self.project_path / project_name
        if project_dir.exists():
            raise FileExistsError(
                f"Project directory already exists: {project_dir}"
            )

        shutil.copytree(
            src=self.template_path,
            dst=project_dir,
        )
        return project_dir
    
    def __rename_directories(self, project_dir: Path):
        for old_path, new_path in self.renamed_dir.items():
            old_dir = project_dir / old_path
            new_dir = project_dir / new_path
            if old_dir.exists() and old_dir != new_dir:
                new_dir.parent.mkdir(parents=True, exist_ok=True)
                old_dir.rename(new_dir)
                self.__cleanup_empty(old_dir.parent, project_dir)

    def __cleanup_empty(self, dir_path: Path, stop_at: Path):
        if dir_path == stop_at or not dir_path.exists():
            return
        if any(dir_path.iterdir()):
            return

        dir_path.rmdir()
        self.__cleanup_empty(dir_path.parent, stop_at)