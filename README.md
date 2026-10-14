# Create Project

A small, cross-platform GUI tool that scaffolds new projects. Pick a project type, fill in a
few fields, and the tool generates the project in the current folder — together with a
`guidance.txt` file containing the exact commands you need to build, test and run it.

Generation runs on a background thread, so the window stays responsive and an indeterminate
progress bar is shown until the project is ready.

Two generation strategies are supported:

- **Command based** — delegates to an external CLI (`mvn`, `gradle`, `npx create-next-app`, …).
- **Template based** — copies a prepared project skeleton out of `boilerplate/` and rewrites
  its placeholders (currently used for Android).

New to the codebase and want to add a project type? See [DEVELOP.md](DEVELOP.md).

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Supported Project Types](#supported-project-types)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Project Fields](#project-fields)
- [Generated Output](#generated-output)
- [Context Menu Integration](#context-menu-integration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- Single-window Tkinter GUI — a project type dropdown plus a form that is rendered dynamically
  from the selected creator's field definitions.
- Project generation runs off the UI thread, with an indeterminate progress bar and a busy
  cursor while it works.
- Works on Windows, macOS and Linux. The Android SDK path is auto-detected per platform.
- Runs entirely from a folder: the target directory comes from `sys.argv[1]`, so the tool can be
  launched from a file manager context menu.
- Every generated project gets a `guidance.txt` with commands tailored to that project type.
  The Android notes cover build, run, test, release packaging, quick edits and troubleshooting.
- Zero runtime dependencies — only the Python standard library (Tkinter ships with CPython).
- Template-based creators can also *generate* files from scratch (for example
  `local.properties`), not just copy and rewrite existing ones.

---

## How It Works

The UI is fully decoupled from the generation logic, and the two communicate through a
controller:

```text
main.py  ──>  ProjectController  ──>  View (Tkinter)  +  BackgroundRunner
                     │                                          │
                     └──>  Registry  ──>  CreateProject.execute() ┘
```

- `ProjectController` (`src/controller.py:5`) wires the view, the registry and a runner together.
  It never touches Tkinter directly — it only talks to the `View` interface and to a
  `BackgroundRunner` abstraction.
- `BackgroundRunner` (`src/concurrency/runner.py:4`) runs the creation work off the UI thread and
  delivers `on_success` / `on_error` callbacks back on the UI thread via `View.post`.
- `CreateProject.execute()` (`src/create/creator.py:22`) validates the inputs, runs the
  strategy-specific work and writes `guidance.txt`.

Because the view is an abstract interface, a different front-end (CLI, web) only needs a new
`View` implementation — no creator changes. See
[Architecture](DEVELOP.md#architecture) for the full picture.

---

## Supported Project Types

| Type | Strategy | Tool / Template | Description |
|------|----------|-----------------|-------------|
| Maven | command | `mvn archetype:generate` | Java library project with JUnit 5 notes |
| Gradle | command | `gradle init` | Java library, Groovy or Kotlin DSL |
| NestJS | command | `@nestjs/cli` | TypeScript backend framework (Node.js) |
| NextJS | command | `create-next-app` | React full-stack framework |
| Android | template | `boilerplate/android-studio` | Android app skeleton (Java, AGP 9, Gradle KTS) |

The registry that maps the GUI label to a creator class lives in `src/create/registry.py:6`.

---

## Requirements

- **Python 3.13+** — the code uses `match` statements, `typing.override` and `@override` (3.12+).
- Per project type:
  - Maven → `mvn` on `PATH`
  - Gradle → `gradle` on `PATH`
  - NestJS / NextJS → Node.js and the respective CLI (run via `npx`)
  - Android → JDK 17+, Android SDK, and `ANDROID_HOME` (or `ANDROID_SDK_ROOT`) set
- **PyInstaller** — only needed to build the standalone executable.

There is no `requirements.txt`: the application imports nothing outside the standard library.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/fishsauce-05/create-project.git
cd create-project
```

### 2. Run from source

```bash
python src/main.py
```

`src` is automatically on `sys.path` because the entry script lives there, so the `create.*`,
`views.*` and `concurrency.*` imports resolve without any install step.

### 3. (Optional) Build the executable

```bash
pip install pyinstaller
build.bat          # Windows: pyinstaller src/main.spec --distpath=dist --workpath=build
```

The result is `dist/main.exe` (Windows) or `dist/main` (Linux/macOS). See
[Build Distribution](DEVELOP.md#build-distribution) for details.

---

## Usage

```bash
python src/main.py                 # current folder
python src/main.py "C:\Projects"   # explicit target folder
```

1. Choose a project type from the dropdown. Selecting a type immediately renders that type's
   form.
2. Fill in the fields. Defaults are pre-filled — leave a field blank to accept its default.
3. Press **Submit**. A progress bar appears while the project is generated on a background
   thread. On success the window closes; on failure the error is shown in a dialog and you can
   correct the input and try again.

The project is created at `<target folder>/<project name>`.

---

## Project Fields

Each creator declares a `requirements` dictionary. The GUI renders one row per entry:

```python
{
    "package_name": {
        "type": "str",                   # "str" | "radio" | "checkbox" | "dropdown"
        "prompt": "Enter the package name",   # label shown next to the input
        "name": "package name",          # name used in the "required field" error
        "default": "com.fishsauce.app",  # pre-filled value; fallback for blank input
        "required": True,                # blank input raises an error instead of using the default
        "option": ["a", "b"]             # choices, required for "radio" and "dropdown"
    }
}
```

| Field key | Meaning |
|-----------|---------|
| `type` | Widget type: `str`, `radio`, `checkbox` or `dropdown` |
| `prompt` | Label text |
| `name` | Human-readable field name used in validation errors |
| `default` | Pre-filled value and fallback when the input is empty |
| `required` | When `true`, the field must not be blank (ignored for `checkbox`) |
| `option` | List of choices, required for `radio` and `dropdown` |

Field handling lives in `src/views/base/field.py:6` (`Field.value()` strips whitespace and falls
back to the default) and `src/views/tkinter/tkinter_view.py:50` (`render_form`).

### Android fields

| Field | Required | Default |
|-------|----------|---------|
| `project_name` | yes | — (a folder is created for the project) |
| `package_name` | no | `com.fishsauce.app` |
| `application_name` | no | `Fishsauce and Cotton` |
| `sdk_directory` | no | auto-detected from `ANDROID_HOME` / `ANDROID_SDK_ROOT`, otherwise the platform default |

---

## Generated Output

For the Android type, generating a project called `MyApp` with package `com.acme.myapp` produces:

```text
<target>/MyApp/
├── app/
│   ├── build.gradle.kts              # namespace + applicationId rewritten to com.acme.myapp
│   └── src/
│       ├── main/
│       │   ├── AndroidManifest.xml
│       │   ├── java/com/acme/myapp/          # renamed from com/fishsauce/app
│       │   │   ├── MainActivity.java
│       │   │   └── SayHelloActivity.java      # typewriter demo
│       │   ├── keepRules/rules.keep           # R8 keep rules
│       │   └── res/                          # layouts, strings, themes, icons
│       ├── test/java/com/acme/myapp/
│       │   └── ExampleUnitTest.java
│       └── androidTest/java/com/acme/myapp/
│           ├── ExampleInstrumentedTest.java
│           └── SayHelloTest.java
├── gradle/
│   ├── libs.versions.toml            # version catalog
│   └── wrapper/                      # Gradle 9.5.0 wrapper
├── build.gradle.kts
├── settings.gradle.kts               # includes :app, sets rootProject.name
├── gradle.properties
├── local.properties                  # generated from the sdk_directory field
├── gradlew / gradlew.bat
└── guidance.txt                      # build / run / test commands
```

`guidance.txt` is always written by `CreateProject._create_guidance()`
(`src/create/creator.py:40`) through `FileWriter.insert_one`, which de-indents the creator's
`readme` block and strips it.

---

## Context Menu Integration

### Windows

Move the executable to a permanent location, for example
`C:\Tools\CreateProject\create-project.exe`, then create `install-context-menu.reg`:

```reg
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\Directory\Background\shell\CreateProject]
@="Create Project"
"Icon"="C:\\Tools\\CreateProject\\create-project.exe"

[HKEY_CLASSES_ROOT\Directory\Background\shell\CreateProject\command]
@="\"C:\\Tools\\CreateProject\\create-project.exe\" \"%V\""
```

Double-click the file and confirm. Right-click in any folder background → **Create Project**;
the current folder is passed as `sys.argv[1]`.

### Linux

Make the binary executable and wire it into your file manager / desktop environment:

```bash
chmod +x dist/main
/path/to/main "%f"
```

The same works for a `.desktop` launcher or a Nautilus/Dolphin custom action.

---

## Troubleshooting

| Symptom | Cause / Fix |
|---------|-------------|
| `SDK location not found. Define a valid SDK location with an ANDROID_HOME environment variable...` | `sdk_directory` was blank, so `new_files` wrote `sdk.dir = ` with an empty value. Export `ANDROID_HOME` / `ANDROID_SDK_ROOT` or type a real path. |
| `Project directory already exists: ...` | The target folder name is taken. Pick a different `project_name` or delete the folder. |
| `Missing required inputs: project name` | A required field was submitted blank. |
| `ModuleNotFoundError: No module named 'create'` | Run as `python src/main.py` (not `python create/...`). |
| `FileNotFoundError` after selecting Android | Run from a checkout that contains `boilerplate/`, or use a PyInstaller build. |
| Progress bar never stops and no error dialog appears | The background worker failed while reporting its result, so the UI callback never ran. Run from a terminal (`python src/main.py`) to see the traceback, since the GUI build hides it. |
| Build fails with stale package names | Old Gradle caches survived the rename — run `./gradlew clean` in the generated project. |
| `rootProject.name` still says `Fishsauce & Cotton` | The boilerplate Gradle project name is not renamed (see [DEVELOP.md](DEVELOP.md#known-caveats)). Edit `settings.gradle.kts` manually. |
| Exe is unexpectedly large | Build artifacts left inside `boilerplate/`; delete `boilerplate/android-studio/{app/build,build,.gradle,.idea}`. |
| `guidance.txt` missing | Generation failed before `_create_guidance()`; the error dialog shows the cause. |

---

## Contributing

Contributions are welcome — ideas, improvements and bug fixes via issues or pull requests.
Development setup, architecture and the guide to adding a new project type are documented in
[DEVELOP.md](DEVELOP.md).

---

## License

MIT
