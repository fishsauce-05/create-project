# Create Project

A Tkinter-based GUI tool for quickly scaffolding new projects. Select a project type, fill in the required fields, and the tool generates the project structure along with a `guidance.txt` containing useful commands.

## Supported Project Types

| Type | Tool | Description |
|------|------|-------------|
| Maven | `mvn archetype:generate` | Java library project with JUnit 5 |
| Gradle | `gradle init` | Java library with Groovy or Kotlin DSL |
| NestJS | `@nestjs/cli` | TypeScript backend framework (Node.js) |
| NextJS | `create-next-app` | React full-stack framework |
| Android | Python file generator | Android app skeleton with AGP, Kotlin or Java |

## Requirements

- Python 3.13+
- For Maven/Gradle projects: `mvn` and/or `gradle` must be installed and available in `PATH`
- For NestJS/NextJS projects: Node.js must be installed
- For Android projects: JDK 17+, Android SDK, and `ANDROID_HOME` environment variable set
- PyInstaller (for building the `.exe` distribution)

## Usage

```bash
python main.py
```

The GUI will open. Select a project type from the dropdown, fill in the required fields, and click Submit.

## Build Distribution

```bash
pyinstaller main.spec --noconfirm
```

The output executable will be placed in `dist/main.exe`.

## Project Structure

```
create-project/
├── main.py                  # Entry point
├── main.spec                # PyInstaller spec
├── registry.py              # Maps project types to command classes
├── views/
│   ├── view.py              # Abstract View base class
│   └── tkinter_view.py      # Tkinter GUI implementation
└── commands/
    ├── cmd.py               # Abstract Command base class (execute, guidance)
    ├── maven.py              # Maven project scaffolding
    ├── gradle.py             # Gradle project scaffolding
    ├── nestjs.py             # NestJS project scaffolding
    ├── nextjs.py             # Next.js project scaffolding
    └── android.py            # Android project scaffolding
```

## Adding a New Project Type

1. Create a new file in `commands/` extending `Cmd`:

```python
from commands.cmd import Cmd
from typing import override

class MyFramework(Cmd):
    def __init__(self):
        super().__init__()

    @override
    @property
    def requirements(self):
        return {
            "project_name": {
                "type": "str",
                "prompt": "Enter the project name:",
                "required": True
            }
        }

    @override
    @property
    def readme(self):
        return "Usage notes written to guidance.txt"

    @override
    @property
    def command(self):
        return f"your-cli create {self.user_input.get('project_name', '')}"
```

2. Register it in `registry.py`:

```python
from commands import myframework

self.fields = {
    ...,
    "MyFramework": myframework.MyFramework
}
```

## License

MIT
