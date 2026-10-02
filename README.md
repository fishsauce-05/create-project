# Create Project

A small cross-platform GUI tool that scaffolds new projects. Pick a project type, fill in a
few fields, and the tool generates the project in the current folder — together with a
`guidance.txt` file containing the exact commands you need to build, test and run it.

Two generation strategies are supported:

- **Command based** — delegates to an external CLI (`mvn`, `gradle`, `npx create-next-app`, …)
- **Template based** — copies a prepared project skeleton out of `boilerplate/` and rewrites
  its placeholders (currently used for Android)

---

## Table of Contents

- [Features](#features)
- [Supported Project Types](#supported-project-types)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Project Fields](#project-fields)
- [Generated Output](#generated-output)
- [Architecture](#architecture)
- [Helpers](#helpers)
- [Android Template Deep Dive](#android-template-deep-dive)
- [Adding a New Project Type](#adding-a-new-project-type)
- [Build Distribution](#build-distribution)
- [Context Menu Integration](#context-menu-integration)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- Single window Tkinter GUI — project type dropdown + dynamically rendered form.
- Works on Windows, macOS and Linux (the Android SDK path is auto-detected per platform).
- Runs entirely from a folder: the target directory comes from `sys.argv[1]`, so the tool can
  be launched from a file manager context menu.
- Every generated project gets a `guidance.txt` with commands tailored to that project type. The
  Android notes cover build, run, test, release packaging, quick edits and troubleshooting.
- Zero runtime dependencies — only the Python standard library (Tkinter ships with CPython).
- Template-based creators can also *generate* files from scratch (`local.properties`), not just
  copy and rewrite them.

---

## Supported Project Types

| Type | Strategy | Tool / Template | Description |
|------|----------|-----------------|-------------|
| Maven | command | `mvn archetype:generate` | Java library project with JUnit 5 notes |
| Gradle | command | `gradle init` | Java library, Groovy or Kotlin DSL |
| NestJS | command | `@nestjs/cli` | TypeScript backend framework (Node.js) |
| NextJS | command | `create-next-app` | React full-stack framework |
| Android | template | `boilerplate/android-studio` | Android app skeleton (Java, AGP 9, Gradle KTS) |

The registry lives in `src/create/registry.py:6` and maps the GUI label to a creator class.

---

## Requirements

- **Python 3.13+** — the code uses `match` statements and `typing.override` (3.12+).
- Per project type:
  - Maven → `mvn` in `PATH`
  - Gradle → `gradle` in `PATH`
  - NestJS / NextJS → Node.js + the respective CLI (`npx`)
  - Android → JDK 17+, Android SDK, and `ANDROID_HOME` (or `ANDROID_SDK_ROOT`) set
- **PyInstaller** — only needed if you want to build the standalone executable.

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

`src` is automatically on `sys.path` because the script lives there, so the `create.*` and
`views.*` imports resolve without any install step.

### 3. (Optional) Build the executable

```bash
pip install pyinstaller
build.bat          # Windows: pyinstaller src/main.spec --distpath=dist --workpath=build
```

The result is `dist/main.exe` (Windows) or `dist/main` (Linux/macOS). See
[Build Distribution](#build-distribution).

---

## Usage

```bash
python src/main.py                 # current folder
python src/main.py "C:\Projects"   # explicit target folder
```

1. Choose a project type from the dropdown. Selecting a type immediately renders that type's form.
2. Fill in the fields (defaults are pre-filled; leave them blank to accept the default).
3. Press **Submit**. On success the window closes; on failure the error is shown in a dialog.

The project is created at `<target folder>/<project_name>`.

---

## Project Fields

Each creator declares a `requirements` dictionary. The GUI renders one row per entry:

```python
{
    "package_name": {
        "type": "str",                 # "str" (text field) or "radio" (radio buttons)
        "prompt": "Enter the package name",   # label shown next to the input
        "name": "project name",        # name used in the "this field is required" error
        "default": "com.fishsauce.app",# pre-filled value; also the fallback for blank input
        "required": True,              # blank input raises an error instead of using the default
        "option": ["a", "b"]           # radio buttons only
    }
}
```

| Field key | Meaning |
|-----------|---------|
| `type` | Widget type: `str` or `radio` |
| `prompt` | Label text |
| `name` | Human readable field name used in validation errors |
| `default` | Pre-filled value and fallback when the input is empty |
| `required` | When `true`, the field must not be blank |
| `option` | List of choices, required for `radio` |

Field handling lives in `src/views/base/field.py` (`Field.value()` strips whitespace and falls
back to the default) and `src/views/tkinter/tkinter_view.py:38` (`render_form`).

### Android fields

| Field | Required | Default |
|-------|----------|---------|
| `project_name` | yes | — (folder created for the project) |
| `package_name` | no | `com.fishsauce.app` |
| `application_name` | no | `Fishsauce and Cotton` |
| `sdk_directory` | no | auto-detected from `ANDROID_HOME` / `ANDROID_SDK_ROOT`, otherwise the platform default |

---

## Generated Output

For the Android type, generating a project called `MyApp` with package `com.acme.myapp` produces:

```text
<target>/MyApp/
├── app/                       # Android application module
│   ├── build.gradle.kts       # namespace + applicationId rewritten to com.acme.myapp
│   └── src/
│       ├── main/java/com/acme/myapp/     # package folder renamed from com/fishsauce/app
│       │   ├── MainActivity.java
│       │   ├── SayHelloActivity.java    # typewriter demo
│       │   └── keepRules/rules.keep      # R8 keep rules
│       ├── test/java/com/acme/myapp/
│       └── androidTest/java/com/acme/myapp/
├── gradle/wrapper/            # Gradle 9.5.0 wrapper
├── local.properties           # written from scratch, see `new_files`
├── settings.gradle.kts        # includes :app, sets rootProject.name
├── gradlew / gradlew.bat
└── guidance.txt               # build / run / test commands
```

`guidance.txt` is always written by `CreateProject._create_guidance()` (`src/create/creator.py:40`)
through `FileWriter.insert_one`, which de-indents the creator's `readme` block and strips it.

---

## Architecture

```text
main.py ──> views (Tkinter)  ──> create.registry.Registry ──> creator instance
                                                                   │
                                                     CreateProject.execute()
                                                                   │
                              ┌────────────────────────────────────┴─────────────────────┐
                              ▼                                                          ▼
            CreateProjectByCommand (cmd/)                        CreateProjectByTemplate (template/)
            runs `self.command` via subprocess                   copy + rename + text-replace + new files
```

### `CreateProject` — `src/create/creator.py`

Abstract base class.

- `project_path` — target folder, taken from `sys.argv[1]` or `.`
- `user_input` — dict filled in by the GUI
- `file` — a `FileWriter` used for `guidance.txt`
- `requirements` / `readme` — abstract properties
- `execute()` — validates required inputs, calls `_do_execute()`, writes `guidance.txt`

### `CreateProjectByCommand` — `src/create/cmd/_base.py`

Runs an external CLI. The `command` string is split on `&&`; a leading `cd <dir>` changes the
working directory for the following commands; each remaining command is executed with
`subprocess.run(..., check=True)`, so a non-zero exit code surfaces as an error dialog.

### `CreateProjectByTemplate` — `src/create/template/_base.py`

Four steps, driven by four abstract properties plus one optional hook:

| Member | Purpose |
|--------|---------|
| `template_path` | Source folder to copy (resolved relative to the repo, or `sys._MEIPASS` when frozen) |
| `renamed_dir` | `{old relative path: new relative path}` — directories are moved |
| `replaced_text` | `{old text: new text}` — plain substring replacement inside text files |
| `ignored_patterns` | `fnmatch` patterns of files that must not be rewritten |
| `new_files` (optional) | `{absolute Path: content}` — files written **after** the copy/rename/rewrite steps |

```text
__copy_template()          DirectoryManager.copy_template()
                          shutil.copytree, raises FileExistsError if the folder exists
self.dirs.rename_directories(...)
                          Path.rename() per entry, then _cleanup_empty() prunes
                          the leftover empty folders
self.text.replace(...)     TextReplacer walks every file and applies replaced_text
self.file.insert_many(...) FileWriter writes new_files (skipped when it is None)
```

Because `new_files` runs last, its content is never rewritten by `replaced_text`. That is how the
Android creator writes `local.properties` (which is git-ignored in the boilerplate and therefore
absent from a fresh clone) instead of patching a `sdk.dir=` prefix that might not be there.

### Views — `src/views/`

- `base/view.py` — `View` interface: `select_project_type`, `select_project_input`, `render_form`, `run`, `close`, `show_error`
- `base/ui_input.py` + `tkinter/tkinter_input.py` — widget factories (`dropdown_input`, `str_input`, `radio_input`)
- `base/field.py` — value reader with default fallback
- `tkinter/tkinter_view.py` — form rendering and required-field validation

The view layer is fully abstracted, so a different UI (CLI, web) only needs a new `View`
implementation — no creator changes.

---

## Helpers

`src/create/helper/` holds the reusable pieces. All three are re-exported from
`src/create/helper/__init__.py`, so creators import them from `..helper`.

### `DirectoryManager` — `src/create/helper/directory_manager.py`

| Method | Behaviour |
|--------|-----------|
| `copy_template(src, dst)` | `shutil.copytree`; raises `FileExistsError(f"Project directory already exists: {dst}")` if `dst` exists |
| `rename_directories(project_dir, renamed_dirs)` | `Path.rename()` for each `{old: new}` entry, creating the target parent first; skips entries where `old == new` or `old` is absent |
| `_cleanup_empty(dir_path, stop_at)` | Recursively `rmdir()`s empty parents up to (but not including) `stop_at` |

### `FileWriter` — `src/create/helper/file_writer.py`

| Method | Behaviour |
|--------|-----------|
| `insert_one(path, content)` | `textwrap.dedent(content).strip()`, then `Path.write_text(..., encoding="utf-8")` |
| `insert_many(files)` | No-op when `files` is `None`, otherwise `insert_one` per entry |

Both creators own a `FileWriter` (`self.file`) — `CreateProject` for `guidance.txt`,
`CreateProjectByTemplate` for `new_files`.

Note that `insert_one` does **not** create parent directories. Templates must therefore return
fully-formed paths whose parents already exist in the copied skeleton.

### `TextReplacer` — `src/create/helper/text_replacer.py`

Walks `project_dir.rglob("*")` and applies every `{old: new}` substring mapping to each decodable
text file, writing only when the content actually changed. It skips:

- `TextReplacer.DEFAULT_IGNORE` — `.git`, `build`, and images (`*.png`, `*.jpg`, `*.jpeg`,
  `*.webp`, `*.ico`, `*.gif`, `*.svg`)
- anything the creator adds via `ignored_patterns`
- files that raise `UnicodeDecodeError` or `PermissionError` on read (e.g. `gradle-wrapper.jar`)

Matching is `fnmatch` against the **relative, POSIX-style** path, so a bare pattern such as
`.git` only matches at the root — pair it with `.git/*` and `*/.git/*` to cover every depth.

---

## Android Template Deep Dive

Implementation: `src/create/template/android.py`.

The Android creator does **not** shell out to any CLI. It copies the skeleton in
`boilerplate/android-studio/` and rewrites it, which makes generation fast and fully offline.

### Boilerplate contents

| Item | Value |
|------|-------|
| Android Gradle Plugin | 9.3.1 (`gradle/libs.versions.toml`) |
| Gradle wrapper | 9.5.0 |
| Gradle DSL | Kotlin DSL (`.kts`), AGP 9 `compileSdk { version = release(37) }` |
| `compileSdk` / `targetSdk` | 37 |
| `minSdk` | 24 |
| Java source/target | 11 |
| Runtime deps | `activity-ktx`, `appcompat`, `constraintlayout`, `material` (version catalog aliases) |
| Tests | JUnit 4.13.2 + Robolectric 4.11.1 + `androidx.test:core` 1.5.0 + `androidx.test.ext:junit` 1.3.0 + Espresso 3.7.0 |
| UI | `home.xml` (live layout), `activity_main.xml` (sample), `SayHelloActivity` (typewriter demo) |
| R8 keep rules | `app/src/main/keepRules/rules.keep` |
| `org.gradle.configuration-cache` | `true` in `gradle.properties` |
| ViewBinding | disabled |
| `local.properties` | **not tracked** — git-ignored in the boilerplate, generated per-project |

### Placeholders

Module constants at `src/create/template/android.py:7`:

| Constant | Value | Replaces occurrences of |
|----------|-------|-------------------------|
| `DEFAULT_PACKAGE` | `com.fishsauce.app` | `namespace`, `applicationId`, `package` declarations, the instrumentation assert |
| `DEFAULT_APP_NAME` | `Fishsauce and Cotton` | `app_name` in `strings.xml` |

Each mapping entry is dropped when the target value equals the default, so untouched files are
never rewritten. There is deliberately **no** display-text constant: `It's Fishsauce ~(￣▽￣)~` is
hard-coded in `home.xml` / `activity_main.xml` and is not renamed (see caveats).

### Directory renaming

`renamed_dir` converts the package name to a path (`com.acme.myapp` → `com/acme/myapp`) and
moves the three source roots:

```text
app/src/main/java/com/fishsauce/app      -> app/src/main/java/<new package>
app/src/test/java/com/fishsauce/app      -> app/src/test/java/<new package>
app/src/androidTest/java/com/fishsauce/app -> app/src/androidTest/java/<new package>
```

If the package is unchanged the mapping is empty and no directories move. Leftover empty
folders (`com/fishsauce/`) are pruned afterwards. The mapping returns `{}` when old and new
paths are identical.

### SDK path resolution and `local.properties`

`__get_android_sdk_directory()` resolves the *default* shown in the GUI, in order:

1. `ANDROID_HOME`, then `ANDROID_SDK_ROOT` (normalised to forward slashes)
2. `~/AppData/Local/Android/Sdk` (Windows)
3. `~/Library/Android/sdk` (macOS)
4. `~/Android/Sdk` (Linux)
5. `""` (unknown platform)

`local.properties` is **not** part of the tracked boilerplate (the boilerplate `.gitignore`
lists it), so a fresh clone does not contain it. Instead of patching a `sdk.dir=` prefix, the
Android creator generates the whole file via `new_files`:

```python
@property
def new_files(self):
    project_dir = self.project_path / project_name / "local.properties"
    return {Path(project_dir): f"sdk.dir = {sdk_dir}"}
```

Because `FileWriter.insert_one` de-indents and strips, the result is the single line
`sdk.dir = <path>`. Backslashes in the entered path are converted to `/`.

An empty `sdk_directory` still produces a file — just with an empty value (`sdk.dir = `) — which
Gradle rejects with `SDK location not found`. Export `ANDROID_HOME` or type a real path.

### Ignored patterns

In addition to the `TextReplacer` defaults (`.git`, `build`, images), Android skips
`.gradle`, `*.jar`, `*.jks`, `*.keystore` and `.idea` so binaries and IDE state are copied
untouched.

### `guidance.txt` contents

The `readme` property (`src/create/template/android.py:64`) is a six-section cheat sheet in
Vietnamese, written to every generated project:

1. **Build & verify** — `build`, `assembleDebug`, `test`, `lintDebug`, `clean`, `:app:tasks`,
   low-memory and offline flags, configuration-cache toggle
2. **Run** — `installDebug`, APK path, manual `adb install`, `adb devices`, emulator/`adb logcat`
   / `force-stop` / `uninstall` recipes
3. **Test** — unit vs. instrumented tasks, test libraries, HTML/XML report paths
4. **Release packaging** — `keytool` keystore generation, a `signingConfigs` + `buildTypes.release`
   snippet, `assembleRelease`, `bundleRelease`, output paths
5. **Quick edits** — where to change layout, strings, theme, SDK versions, package, dependencies
6. **Troubleshooting** — `SDK location not found`, dependency/daemon/package errors, `--stacktrace`

### Known caveats

- **`rootProject.name` is not renamed.** `settings.gradle.kts` contains `Fishsauce & Cotton`
  while `DEFAULT_APP_NAME` is `Fishsauce and Cotton`, so choosing an application name rewrites
  `strings.xml` but leaves the Gradle project name as `Fishsauce & Cotton`. Align the two (or
  drop the `& Cotton` suffix from the boilerplate) for a fully clean rename.
- **Display text is not renamed.** `home.xml` and `activity_main.xml` hard-code
  `It's Fishsauce ~(￣▽￣)~`. If you want it to follow `application_name`, move it into
  `strings.xml` and add a placeholder constant back.
- **Text replacement is case-sensitive**, which is why lowercase `fishsauce` inside
  `ExampleUnitTest` is intentionally left alone.
- **`new_files` overwrites unconditionally.** Returning a path that already exists in the
  skeleton replaces it, so only use it for files that are absent or fully owned by the creator.
- **Stale Gradle output in `boilerplate/`** (`app/build/`, `.gradle/`, `.idea/`, `*.log`) is
  git-ignored but still copied into every generated project — roughly 41 MB in total. Delete
  those folders before distributing a PyInstaller build.

---

## Adding a New Project Type

### Command based

1. Create `src/create/cmd/myframework.py` extending `CreateProjectByCommand`:

```python
from ._base import CreateProjectByCommand as Cmd
from typing import override

class MyFramework(Cmd):
    @override
    @property
    def requirements(self):
        return {
            "project_name": {
                "type": "str",
                "prompt": "Enter the project name:",
                "name": "project name",
                "required": True
            }
        }

    @override
    @property
    def readme(self):
        return "Commands written to guidance.txt"

    @override
    @property
    def command(self):
        project_name = self.user_input.get("project_name", "")
        return f"your-cli create {project_name}"
```

2. Export it in `src/create/cmd/__init__.py`.
3. Register it in `src/create/registry.py`:

```python
from create.cmd import MyFramework

self.fields = {
    ...,
    "MyFramework": MyFramework,
}
```

### Template based

1. Add `boilerplate/<your-platform>/` with sensible placeholder values.
2. Create `src/create/template/myplatform.py` extending `CreateProjectByTemplate` and implement
   `template_path`, `renamed_dir`, `replaced_text`, `ignored_patterns`, `requirements`, `readme`
   (see `src/create/template/android.py` as the reference implementation).
3. Optionally override `new_files` for files that must be generated rather than copied — useful
   for machine-local config such as `local.properties`:

```python
@override
@property
def new_files(self) -> dict[Path, str]:
    if not self.new_files_enabled:
        return None
    target = self.destination / "local.properties"
    return {Path(target): f"profile = {self.profile_name}"}
```

4. Export it in `src/create/template/__init__.py`.
5. Register it in `src/create/registry.py`.

The skeleton is bundled into the executable by `datas=[(str(project_root / 'boilerplate'), 'boilerplate')]`
in `src/main.spec`, so a new template folder is picked up automatically on the next build.

---

## Build Distribution

```bash
build.bat
# equivalent to:
pyinstaller src/main.spec --distpath=dist --workpath=build
```

Output:

```text
dist/
└── main.exe       # Windows
└── main           # Linux / macOS
```

When frozen, `template_path` resolves to `sys._MEIPASS` so the bundled boilerplate is used.

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
```

```bash
/path/to/main "%f"
```

The same works for a `.desktop` launcher or a Nautilus/Dolphin custom action.

---

## Project Structure

```text
create-project/
├── src/
│   ├── create/
│   │   ├── creator.py            # CreateProject ABC: validate, execute, write guidance.txt
│   │   ├── registry.py           # GUI label -> creator class
│   │   ├── cmd/                  # command-based creators (maven, gradle, nestjs, nextjs)
│   │   │   └── _base.py
│   │   ├── template/             # template-based creators (android)
│   │   │   ├── _base.py          # copy + rename + text-replace + new-files pipeline
│   │   │   └── android.py
│   │   └── helper/               # re-exported from helper/__init__.py
│   │       ├── directory_manager.py  # copytree, directory renaming, empty-folder pruning
│   │       ├── file_writer.py        # dedent + write one/many files
│   │       └── text_replacer.py      # substring replacement with ignore patterns
│   ├── views/
│   │   ├── base/                 # View / UIInput / Field abstractions
│   │   └── tkinter/              # Tkinter implementation
│   ├── main.py                   # entry point: view + registry wiring
│   └── main.spec                 # PyInstaller spec (bundles boilerplate/)
├── boilerplate/
│   └── android-studio/           # Android skeleton copied for new projects
├── build.bat
└── README.md
```

---

## Troubleshooting

| Symptom | Cause / Fix |
|---------|-------------|
| `SDK location not found. Define a valid SDK location with an ANDROID_HOME environment variable...` | `sdk_directory` was blank, so `new_files` wrote `sdk.dir = ` with an empty value. Export `ANDROID_HOME` / `ANDROID_SDK_ROOT` or type a real path. |
| `Project directory already exists: ...` | The target folder name is taken. Pick a different `project_name` or delete the folder. |
| `Missing required inputs: project name` | Submitted a blank required field. |
| `ModuleNotFoundError: No module named 'create'` | Run as `python src/main.py` (not `python create/...`) or install the package. |
| `FileNotFoundError` after selecting Android | Run from a checkout that contains `boilerplate/`, or use a PyInstaller build. |
| Build fails with stale package names | Old Gradle caches survived the rename — run `./gradlew clean` in the generated project. |
| `rootProject.name` still says `Fishsauce & Cotton` | `DEFAULT_APP_NAME` is `Fishsauce and Cotton`, so `settings.gradle.kts` is not matched. Edit it manually or align the two strings. |
| Exe is unexpectedly large | Build artifacts left inside `boilerplate/`; delete `boilerplate/android-studio/{app/build,build,.gradle,.idea}`. |
| `guidance.txt` missing | Generation failed before `_create_guidance()`; the error dialog shows the cause. |
| `FileNotFoundError` from `FileWriter.insert_one` | `new_files` returned a path whose parent directory does not exist — `insert_one` does not create parents. |

---

## Contributing

Contributions are welcome — ideas, improvements and bug fixes via issues or pull requests.

Guidelines:

- Follow the existing `Cmd` / `CreateProjectByTemplate` structure.
- Register new project types in `src/create/registry.py`.
- Keep placeholder constants in sync with the boilerplate they replace.
- Put reusable filesystem logic in `src/create/helper/` rather than inlining it in a creator.
- Keep the code simple, readable and consistent with the surrounding style.

---

## License

MIT
