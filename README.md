# Create Project

A GUI tool for quickly scaffolding new projects. Select a project type, fill in the required fields, and the tool generates the project structure along with a `guidance.txt` containing useful commands.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/<username>/create-project.git
cd create-project
```

### 2. Build the Application

Make sure Python and PyInstaller are installed:

```bash
pip install pyinstaller
```

Then build the executable:

```bash
pyinstaller main.spec --noconfirm
```

The executable will be generated in:

```text
dist/
└── main.exe       # Windows
```

On Linux, the executable will be generated as:

```text
dist/
└── main
```

---

## Windows Context Menu

To add `Create Project` to the Windows right-click context menu, first build the application as described above.

Move the executable to a permanent location, for example:

```text
C:\Tools\CreateProject\create-project.exe
```

Create a file named `install-context-menu.reg`:

```reg
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\Directory\Background\shell\CreateProject]
@="Create Project"
"Icon"="C:\\Tools\\CreateProject\\create-project.exe"

[HKEY_CLASSES_ROOT\Directory\Background\shell\CreateProject\command]
@="\"C:\\Tools\\CreateProject\\create-project.exe\" \"%V\""
```

Double-click the `.reg` file and confirm the changes.

You can now right-click inside any folder and select:

```text
Create Project
```

The current folder will be passed to the application as the first argument.

For example:

```text
create-project.exe "C:\Users\User\Projects"
```

---

## Linux Context Menu

Linux context-menu integration depends on the desktop environment and file manager being used.

First build the application:

```bash
pyinstaller main.spec --noconfirm
```

Make the executable runnable:

```bash
chmod +x dist/main
```

You can then create a launcher or file-manager action that executes:

```bash
/path/to/create-project "%f"
```

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

## Note for developers

Contributions are always welcome! If you have an idea for a new project type, an improvement, or a bug fix, feel free to open an issue or submit a pull request.
When adding a new project type, please follow the existing Cmd structure and register it in registry.py as described above.
Please keep the code simple, readable, and consistent with the existing project structure.

## License

MIT
