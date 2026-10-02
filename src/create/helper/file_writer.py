from pathlib import Path
import textwrap

class FileWriter:
    def insert_one(self, path: Path, content: str) -> None:
        cleaned = textwrap.dedent(content).strip()
        path.write_text(cleaned, encoding="utf-8")

    def insert_many(self, files: dict[Path, str]) -> None:
        if files == None:
            return
        for file_path, content in files.items():
            self.insert_one(file_path, content)