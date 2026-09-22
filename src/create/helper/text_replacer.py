from pathlib import Path
import fnmatch

class TextReplacer:
    DEFAULT_IGNORE = [
        ".git", ".git/*", "*/.git/*",
        "build", "build/*", "*/build/*",
        "*.png", "*.jpg", "*.jpeg", "*.webp", "*.ico", "*.gif", "*.svg",
    ]

    def replace(
        self,
        project_dir: Path,
        mapping: dict[str, str],
        ignore: list[str] | None = None,
    ) -> None:
        if not mapping:
            return

        ignore_patterns = self.DEFAULT_IGNORE + (ignore or [])

        for file_path in project_dir.rglob("*"):
            if not file_path.is_file():
                continue

            rel_path = file_path.relative_to(project_dir).as_posix()
            if self.__is_ignored(rel_path, ignore_patterns):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                continue

            new_content = content
            for old, new in mapping.items():
                new_content = new_content.replace(old, new)

            if new_content != content:
                file_path.write_text(new_content, encoding="utf-8")

    def __is_ignored(self, rel_path: str, patterns: list[str]) -> bool:
        return any(fnmatch.fnmatch(rel_path, pattern) for pattern in patterns)