# Developing Create Project

This document is for contributors who want to extend or modify Create Project. For end-user
installation and usage, see [README.md](README.md).

- [Development Setup](#development-setup)
- [Architecture](#architecture)
- [Controller and Concurrency](#controller-and-concurrency)
- [CreateProject](#createproject--srccreatecreatorpy)
- [CreateProjectByCommand](#createprojectbycommand--srccreatecmdbasepy)
- [CreateProjectByTemplate](#createprojectbytemplate--srccreatetemplatebasepy)
- [View Layer](#view-layer--srcviews)
- [Helpers](#helpers--srccreatehelper)
- [Android Template in Depth](#android-template-in-depth)
- [Adding a New Project Type](#adding-a-new-project-type)
- [Build Distribution](#build-distribution)
- [Project Structure](#project-structure)
- [Conventions](#conventions)
- [Known Caveats](#known-caveats)

---

## Development Setup

There are no runtime or development dependencies — everything uses the Python standard library.

```bash
python src/main.py                 # run the GUI
python src/main.py "C:\Projects"   # run against an explicit target folder
```

The `src/` directory is placed on `sys.path` by virtue of being the entry script's folder, so
`create.*`, `views.*` and `concurrency.*` import as top-level packages. There is no
packaging/install step.

Two files are intentionally **documentation-only** and are not imported anywhere:

- `src/create/cmd/pattern.py` — annotated template for a command-based creator.
- `src/create/template/pattern.py` — annotated template for a template-based creator.

Copy one of them as the starting point for a new creator.

---

## Architecture

```text
main.py  (composition root)
   │  builds TkinterView, Registry and ThreadedBackgroundRunner(post=view.post)
   ▼
ProjectController (controller.py)
   │
   │  view.select_project_type(types, on_select)      ──► user picks a type
   │  registry.create(type)                           ──► creator instance
   │  view.select_project_input(creator.requirements, on_submit)
   │  on submit:
   │      view.show_progress("Creating project…")
   │      runner.run(creator.execute, on_success, on_error)
   │          on_success ──► view.close_progress() + view.close()
   │          on_error   ──► view.close_progress() + view.show_error(message)
   ▼
CreateProject.execute()  (creator.py, Template Method)
   validate → _do_execute → write guidance.txt
```

The UI and the generation logic never reference each other directly: `ProjectController` drives
the `View` interface and the `BackgroundRunner` interface, while creators know nothing about
either. That is what lets the async plumbing (threads, `root.after`) stay out of the creators
and keeps a future CLI/web view a drop-in replacement.

`execute()` (defined once in `CreateProject`) always runs three steps:

1. `_validate_requirements()` — raise `ValueError` if a `required` field is missing.
2. `_do_execute()` — the strategy-specific work.
3. `_create_guidance()` — write `guidance.txt` from the `readme` property.

Subclasses implement `requirements`, `readme` and `_do_execute()`; they should not override
`execute()`.

---

## Controller and Concurrency

### `ProjectController` — `src/controller.py:5`

The single orchestration point, independent of any concrete UI or threading model.

| Member | Behaviour |
|--------|-----------|
| `run()` (`:11`) | Hands the project types to the view and starts the view's event loop |
| `_select_project_type(type)` (`:18`) | Builds the creator via the registry, then shows its form |
| `_execute(creator, user_input)` (`:25`) | Stores the answers on the creator, shows progress, dispatches `creator.execute` to the runner |
| `_on_success()` (`:34`) | Closes the progress indicator and the window |
| `_on_error(message)` (`:38`) | Closes the progress indicator and shows the error dialog |

### `BackgroundRunner` — `src/concurrency/runner.py:4`

Abstract port for "run this work off the UI thread and call me back":

```python
def run(self, work, on_success, on_error) -> None: ...
```

- `work` — a zero-argument callable that raises on failure.
- `on_success` — called when `work` returns normally.
- `on_error` — called with the raised `Exception`.

The controller depends only on this interface, so tests can substitute a synchronous runner.

### `ThreadedBackgroundRunner` — `src/concurrency/threaded_runner.py:5`

The production adapter. It runs `work` in a `daemon` thread and marshals the callbacks back to
the UI thread through an injected `post` callable:

```python
def _target():
    try:
        work()
    except Exception as e:
        post(lambda: on_error(e))
        return
    self.post(on_success)
```

`post` is `TkinterView.post` (`src/views/tkinter/tkinter_view.py:100`), which wraps
`self.root.after(0, fn)`. This is the only place Tkinter's thread-safety rule ("touch widgets
from the main thread only") is satisfied — everything else stays UI-agnostic.

### `main.py` — composition root

`src/main.py:6` builds the three collaborators and injects them, then runs the controller:

```python
view = TkinterView()
registry = Registry()
runner = ThreadedBackgroundRunner(post=view.post)

ProjectController(view, registry, runner).run()
```

There is no application logic in `main.py` — swapping the view or the runner is a one-line
change here.

---

## `CreateProject` — `src/create/creator.py`

Abstract base class for every creator.

- `project_path` — target folder, taken from `sys.argv[1]` or `.`
- `user_input` — dict filled in by the GUI
- `file` — a `FileWriter` used for `guidance.txt`
- `requirements` / `readme` — abstract properties
- `execute()` (`:22`) — validates required inputs, calls `_do_execute()`, writes `guidance.txt`

`_validate_requirements()` (`:27`) checks that every key with `"required": True` is present in
`user_input`. In practice the Tkinter view also validates before submitting
(`src/views/tkinter/tkinter_view.py:103`), and checkbox fields are excluded from that check.

---

## `CreateProjectByCommand` — `src/create/cmd/_base.py`

Runs an external CLI. `_do_execute()` (`src/create/cmd/_base.py:12`) splits the `command`
string on `&&`. A segment starting with `cd <dir>` changes the working directory for the
segments that follow; every other segment is run with `subprocess.run(..., shell=True,
check=True)`, so a non-zero exit code raises and is surfaced as an error dialog by the
controller.

Subclasses only implement `command`, `requirements` and `readme`. Existing creators:
`Maven`, `Gradle`, `Nest`, `Nextjs` (exported from `src/create/cmd/__init__.py`).

Because the command runs inside the background worker, a long CLI invocation no longer blocks
the UI. Note there is currently **no** stdout/stderr streaming and **no** cancel support — the
progress bar is indeterminate (see [Known Caveats](#known-caveats)).

---

## `CreateProjectByTemplate` — `src/create/template/_base.py`

Four steps, driven by four abstract properties plus one optional hook. `_do_execute()` is at
`src/create/template/_base.py:43`.

| Member | Purpose |
|--------|---------|
| `template_path` | Source folder to copy. Defaults to `<repo root>/boilerplate` (or `sys._MEIPASS/boilerplate` when frozen) |
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
absent from a fresh clone) instead of patching an `sdk.dir=` prefix that might not be there.

---

## View Layer — `src/views/`

The view layer is fully abstracted, so a different UI (CLI, web) only needs a new `View`
implementation — no creator or controller changes.

- `base/view.py` — `View` interface:
  - `select_project_type` (`:6`) / `select_project_input` (`:10`) — render the type dropdown and
    the input form
  - `render_form` (`:26`) — build the form widgets for a `requirements` dict
  - `show_progress` (`:30`) / `close_progress` (`:34`) — show and hide a busy indicator
  - `post` (`:38`) — schedule a callback on the UI thread
  - `run` (`:14`) / `close` (`:18`) / `show_error` (`:22`) — event loop, teardown, error dialog
- `base/specification.py` — frozen dataclasses describing each input: `DefaultSpec`, `StrSpec`,
  `RadioSpec`, `CheckboxSpec`, `DropdownSpec`.
- `base/ui_input.py` — `UIInput.create_input()` (`src/views/base/ui_input.py:22`) maps a
  `type` string to the matching widget factory.
- `base/field.py` — `Field` wraps a getter and applies the default fallback.
- `tkinter/tkinter_input.py` — widget factories (`str_input`, `radio_input`, `checkbox_input`,
  `dropdown_input`).
- `tkinter/tkinter_view.py` — form rendering, required-field validation, submit handling and the
  progress bar.

Supported field types and how they render:

| `type` | Widget | Notes |
|--------|--------|-------|
| `str` | text entry | `default` is pre-filled and used as fallback |
| `radio` | radio buttons | first `option` is the default when no `default` is given |
| `checkbox` | checkbutton | excluded from the required-field check |
| `dropdown` | option menu | `option` list required; fires an `on_select` callback |

### Progress indicator

`TkinterView.show_progress()` (`src/views/tkinter/tkinter_view.py:72`) builds a small frame with
a label and a `ttk.Progressbar(mode="indeterminate")`, then sets a busy cursor.
`close_progress()` (`:90`) stops the animation, destroys the frame and restores the cursor. Both
are invoked by the controller, never by a creator — creators just do their work and raise on
failure.

---

## Helpers — `src/create/helper/`

`src/create/helper/__init__.py` re-exports all three, so creators import them from `..helper`.

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
| `insert_many(files)` | No-op when `files is None`, otherwise `insert_one` per entry |

Both creators own a `FileWriter` (`self.file`) — `CreateProject` for `guidance.txt`,
`CreateProjectByTemplate` for `new_files`.

Note that `insert_one` does **not** create parent directories. Templates must therefore return
fully-formed paths whose parents already exist in the copied skeleton.

### `TextReplacer` — `src/create/helper/text_replacer.py`

Walks `project_dir.rglob("*")` and applies every `{old: new}` substring mapping to each
decodable text file, writing only when the content actually changes. It skips:

- `TextReplacer.DEFAULT_IGNORE` — `.git`, `build`, and images (`*.png`, `*.jpg`, `*.jpeg`,
  `*.webp`, `*.ico`, `*.gif`, `*.svg`)
- anything the creator adds via `ignored_patterns`
- files that raise `UnicodeDecodeError` or `PermissionError` on read (for example
  `gradle-wrapper.jar`)

Matching uses `fnmatch` against the **relative, POSIX-style** path, so a bare pattern such as
`.git` only matches at the root — pair it with `.git/*` and `*/.git/*` to cover every depth.

---

## Android Template in Depth

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
| Runtime deps | `activity-ktx` 1.13.0, `appcompat` 1.7.1, `constraintlayout` 2.1.4, `material` 1.14.0 (version catalog aliases) |
| Tests | JUnit 4.13.2, Robolectric 4.11.1, `androidx.test:core` 1.5.0, `androidx.test:runner` 1.5.2, `androidx.test.ext:junit` 1.3.0, Espresso 3.7.0 |
| UI | `home.xml` (live layout), `activity_main.xml` (sample), `SayHelloActivity` (typewriter demo) |
| R8 keep rules | `app/src/main/keepRules/rules.keep` |
| Release build type | `optimization { enable = false }` |
| `org.gradle.configuration-cache` | `true` in `gradle.properties` |
| ViewBinding | disabled |
| `rootProject.name` | `Fishsauce & Cotton` |
| `local.properties` | **not tracked** — git-ignored in the boilerplate, generated per-project |

### Placeholders

Module constants at `src/create/template/android.py:7`:

| Constant | Value | Replaces occurrences of |
|----------|-------|-------------------------|
| `DEFAULT_PACKAGE` | `com.fishsauce.app` | `namespace`, `applicationId`, `package` declarations, the instrumentation assert |
| `DEFAULT_APP_NAME` | `Fishsauce and Cotton` | `app_name` in `strings.xml` |

Each mapping entry is dropped when the target value equals the default, so untouched files are
never rewritten. There is deliberately **no** display-text constant: `It's Fishsauce ~(￣▽￣)~` is
hard-coded in `home.xml` / `activity_main.xml` and is not renamed (see
[Known Caveats](#known-caveats)).

### Directory renaming

`renamed_dir` (`src/create/template/android.py:187`) converts the package name to a path
(`com.acme.myapp` → `com/acme/myapp`) and moves the three source roots:

```text
app/src/main/java/com/fishsauce/app        -> app/src/main/java/<new package>
app/src/test/java/com/fishsauce/app        -> app/src/test/java/<new package>
app/src/androidTest/java/com/fishsauce/app -> app/src/androidTest/java/<new package>
```

If the package is unchanged the mapping is empty and no directories move. Leftover empty
folders (`com/fishsauce/`) are pruned afterwards.

### SDK path resolution and `local.properties`

`__get_android_sdk_directory()` (`src/create/template/android.py:44`) resolves the *default*
shown in the GUI, in order:

1. `ANDROID_HOME`, then `ANDROID_SDK_ROOT` (normalised to forward slashes)
2. `~/AppData/Local/Android/Sdk` (Windows)
3. `~/Library/Android/sdk` (macOS)
4. `~/Android/Sdk` (Linux)
5. `""` (unknown platform)

`local.properties` is **not** part of the tracked boilerplate (the boilerplate `.gitignore`
lists it), so a fresh clone does not contain it. Instead of patching an `sdk.dir=` prefix, the
Android creator generates the whole file via `new_files`
(`src/create/template/android.py:228`):

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
2. **Run** — `installDebug`, APK path, manual `adb install`, `adb devices`, emulator / `adb
   logcat` / `force-stop` / `uninstall` recipes
3. **Test** — unit vs. instrumented tasks, test libraries, HTML/XML report paths
4. **Release packaging** — `keytool` keystore generation, a `signingConfigs` +
   `buildTypes.release` snippet, `assembleRelease`, `bundleRelease`, output paths
5. **Quick edits** — where to change layout, strings, theme, SDK versions, package, dependencies
6. **Troubleshooting** — `SDK location not found`, dependency/daemon/package errors,
   `--stacktrace`

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
   `template_path`, `renamed_dir`, `replaced_text`, `ignored_patterns`, `requirements` and
   `readme` (see `src/create/template/android.py` as the reference implementation).
3. Optionally override `new_files` for files that must be generated rather than copied — useful
   for machine-local config such as `local.properties`:

```python
@override
@property
def new_files(self) -> dict[Path, str]:
    target = self.project_path / self.user_input.get("project_name", "") / "local.properties"
    return {Path(target): f"sdk.dir = {self.user_input.get('sdk_directory', '')}"}
```

4. Export it in `src/create/template/__init__.py`.
5. Register it in `src/create/registry.py`.

The skeleton is bundled into the executable by
`datas=[(str(project_root / 'boilerplate'), 'boilerplate')]` in `src/main.spec`, so a new
template folder is picked up automatically on the next build.

> Note: `boilerplate/` (the skeleton folder copied into new projects) and
> `src/create/template/` (the Python package holding template-based creators) are two different
> things. A template creator usually lives in the latter and points at a sub-folder of the
> former.

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

When frozen, `template_path` resolves to `sys._MEIPASS/boilerplate` so the bundled skeleton is
used.

---

## Project Structure

```text
create-project/
├── src/
│   ├── main.py                   # composition root: wire view + registry + runner
│   ├── controller.py             # ProjectController: orchestration, UI/thread agnostic
│   ├── concurrency/
│   │   ├── runner.py             # BackgroundRunner port
│   │   └── threaded_runner.py    # ThreadedBackgroundRunner adapter (post to UI thread)
│   ├── create/
│   │   ├── creator.py            # CreateProject ABC: validate, execute, write guidance.txt
│   │   ├── registry.py           # GUI label -> creator class
│   │   ├── cmd/                  # command-based creators (maven, gradle, nestjs, nextjs)
│   │   │   ├── _base.py          # CreateProjectByCommand (subprocess runner)
│   │   │   └── pattern.py        # annotated example (not exported)
│   │   ├── template/             # template-based creators (android)
│   │   │   ├── _base.py          # copy + rename + text-replace + new-files pipeline
│   │   │   ├── android.py
│   │   │   └── pattern.py        # annotated example (not exported)
│   │   └── helper/               # re-exported from helper/__init__.py
│   │       ├── directory_manager.py  # copytree, directory renaming, empty-folder pruning
│   │       ├── file_writer.py        # dedent + write one/many files
│   │       └── text_replacer.py      # substring replacement with ignore patterns
│   ├── views/
│   │   ├── base/                 # View / UIInput / Field / specification abstractions
│   │   └── tkinter/              # Tkinter implementation
│   └── main.spec                 # PyInstaller spec (bundles boilerplate/)
├── boilerplate/
│   └── android-studio/           # Android skeleton copied for new projects
├── build.bat
├── README.md                     # user guide
└── DEVELOP.md                    # this file
```

---

## Conventions

- Follow the existing `Cmd` / `CreateProjectByTemplate` structure.
- Register new project types in `src/create/registry.py`.
- Keep placeholder constants in sync with the boilerplate they replace.
- Put reusable filesystem logic in `src/create/helper/` rather than inlining it in a creator.
- Declare `project_name` in every `requirements` with `"required": True`; `_create_guidance()`
  and the template copy both depend on it.
- Read answers with `self.user_input.get("<key>", "<default>")` and keep the fallback in sync
  with the `"default"` declared in `requirements`.
- **Never touch widgets (or the `View`) from a creator.** Creation work runs on a background
  thread; UI updates must go through `View.post` / the runner callbacks so they run on the main
  thread.
- Keep the code simple, readable and consistent with the surrounding style.
- Contributions are welcome via issues or pull requests.

---

## Known Caveats

- **The progress bar is indeterminate.** `show_progress` / `close_progress` have no percentage
  or step API, so a command creator cannot report "step 2/5" and stdout/stderr are not streamed
  into the GUI. Adding progress reporting means extending the `View` (and the runner) with a
  progress/log channel.
- **No cancellation.** `ThreadedBackgroundRunner` starts a daemon thread and never keeps a
  handle to the `subprocess`, so a running CLI cannot be cancelled and a half-generated folder
  is not cleaned up on failure.
- **`rootProject.name` is not renamed.** `settings.gradle.kts` contains `Fishsauce & Cotton`
  while `DEFAULT_APP_NAME` is `Fishsauce and Cotton`, so choosing an application name rewrites
  `strings.xml` but leaves the Gradle project name as `Fishsauce & Cotton`. Align the two (or
  drop the `& Cotton` suffix from the boilerplate) for a fully clean rename.
- **Display text is not renamed.** `home.xml` and `activity_main.xml` hard-code
  `It's Fishsauce ~(￣▽￣)~`. To make it follow `application_name`, move it into `strings.xml`
  and add a placeholder constant back.
- **Text replacement is case-sensitive**, which is why lowercase `fishsauce` inside
  `ExampleUnitTest` is intentionally left alone.
- **`new_files` overwrites unconditionally.** Returning a path that already exists in the
  skeleton replaces it, so only use it for files that are absent or fully owned by the creator.
- **Stale Gradle output in `boilerplate/`** (`app/build/`, `.gradle/`, `.idea/`, `*.log`) is
  git-ignored but still copied into every generated project. Delete those folders before
  distributing a PyInstaller build; otherwise the executable is roughly 41 MB larger.
