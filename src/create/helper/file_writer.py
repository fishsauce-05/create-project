from pathlib import Path

class FileWriter:
    def write(self, file_path: Path, content: str):
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)