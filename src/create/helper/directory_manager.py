import shutil
from pathlib import Path

class DirectoryManager:
    def copy_template(self, src: Path, dst: Path) -> Path:
        if dst.exists():
            raise FileExistsError(f"Project directory already exists: {dst}")
        shutil.copytree(src, dst)
        return dst
    
    def rename_directories(self, project_dir: Path, renamed_dirs: dict[str, str]):
        for old_path, new_path in renamed_dirs.items():
            old_dir = project_dir / old_path
            new_dir = project_dir / new_path
            if old_dir.exists() and old_dir != new_dir:
                new_dir.parent.mkdir(parents=True, exist_ok=True)
                old_dir.rename(new_dir)
                self._cleanup_empty(old_dir.parent, project_dir)

    def _cleanup_empty(self, dir_path: Path, stop_at: Path):
        if dir_path == stop_at or not dir_path.exists():
            return
        if any(dir_path.iterdir()):
            return

        dir_path.rmdir()
        self._cleanup_empty(dir_path.parent, stop_at)