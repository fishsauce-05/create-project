"""
PATTERN: template-based creator  (src/create/template)
======================================================

Not exported in __init__.py on purpose — this file is documentation only.

Chain:
    CreateProject (creator.py, ABC)
        -> CreateProjectByTemplate (_base.py, ABC)
            -> YourCreator (template/<your>.py)

execute() flow (defined in creator.py, do NOT override):
    1. _validate_requirements()  -> raises ValueError if a requirement with
       "required": True has no entry in self.user_input
    2. _do_execute()             -> implemented by CreateProjectByTemplate:
         a. copy template_path/<...> into <project_path>/<project_name>
         b. rename directories   with self.renamed_dir
         c. replace text in files with self.replaced_text,
            skipping self.ignored_patterns
         d. create extra files   with self.new_files (if not None)
    3. _create_guidance()        -> writes self.readme to
       <project_path>/<project_name>/guidance.txt

Helpers available on self (created in _base.py):
    self.text  : TextReplacer
    self.file  : FileWriter
    self.dirs  : DirectoryManager

---------------------------------------------------------------------------
WHAT YOU MUST OVERRIDE (all are @property, all return a value)
---------------------------------------------------------------------------

    requirements      -> dict[str, dict[str, str]]
        Input form description. See schema below.

    readme            -> str
        Free text written to guidance.txt after creation.

    renamed_dir       -> dict[str, str]
        {old relative path: new relative path} inside the copied project.
        Return {} when nothing must be renamed.

    replaced_text     -> dict[str, str]
        {old text: new text} applied to every non-ignored file.
        Return {} when nothing must be replaced.

    ignored_patterns  -> list[str]
        Glob-like patterns of files/dirs skipped by the text replacement
        (e.g. ".gradle", ".gradle/*", "*.jar", "*.jks", ".idea", ".idea/*").

Optional (already implemented in _base.py, override only if needed):

    template_path     -> Path
        Defaults to <repo root>/boilerplate (or sys._MEIPASS when frozen).
        Usually overridden as: return super().template_path / "<sub-folder>".

    new_files         -> dict[Path, str]
        {absolute file path: content}. Defaults to None (no extra files).
        Return None when no extra file is needed.

    _do_execute()     -> None
        Override only when the default copy/rename/replace flow is not enough.

---------------------------------------------------------------------------
requirements SCHEMA — important fields and their values
---------------------------------------------------------------------------

    "my_key": {                          # key name used in self.user_input["my_key"]
        "type":     "str" | "radio",     # "str" -> text entry
                                          # "radio" -> radio buttons
        "prompt":   "Enter ...",         # label shown to the user (str)
        "name":     "human readable",    # shown in the missing-input error message
        "required": True | False,        # True  -> validation fails when absent
                                          # False -> user may skip it
        "default":  "fallback value",    # optional; pre-filled / fallback value
        "option":   ["a", "b"],          # REQUIRED when type == "radio"
                                          # first item is the default choice
    }

Rules:
    - "project_name" must always be declared with "required": True,
      because the template is copied to <project_path>/<project_name>.
    - Read answers with self.user_input.get("<key>", <default>) and keep the
      same fallback as the "default" declared in requirements.
    - "name" is what appears in: ValueError("Missing required inputs: ...")
"""

from ._base import CreateProjectByTemplate as Template
from typing import override
from pathlib import Path

class Pattern(Template):
    @override
    @property
    def requirements(self):
        return {
            "project_name": {
                "type": "str",
                "prompt": "Enter the project name:",
                "name": "project name",
                "required": True,
            },
            "language": {
                "type": "radio",
                "prompt": "Select a language:",
                "name": "language",
                "option": ["Vietnamese", "English"],
                "required": True
            },
            "database": {
                "type": "checkbox",
                "prompt": "Do it with database?",
                "name": "database",
                "required": True
            }
        }

    @override
    @property
    def readme(self):
        return "Notes written to guidance.txt."

    @override
    @property
    def template_path(self) -> Path:
        return super().template_path / "pattern"

    @override
    @property
    def renamed_dir(self) -> dict[str, str]:
        return {}

    @override
    @property
    def replaced_text(self) -> dict[str, str]:
        return {"OLD": self.user_input.get("new", "OLD")}

    @override
    @property
    def ignored_patterns(self) -> list[str]:
        return []

    @override
    @property
    def new_files(self) -> dict[Path, str]:
        return None