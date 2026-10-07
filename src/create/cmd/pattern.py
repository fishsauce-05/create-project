"""
PATTERN: command-based creator  (src/create/cmd)
=================================================

Not exported in __init__.py on purpose — this file is documentation only.

Chain:
    CreateProject (creator.py, ABC)
        -> CreateProjectByCommand (_base.py, ABC)
            -> YourCreator (cmd/<your>.py)

execute() flow (defined in creator.py, do NOT override):
    1. _validate_requirements()  -> raises ValueError if a requirement with
       "required": True has no entry in self.user_input
    2. _do_execute()             -> implemented by CreateProjectByCommand:
       splits self.command on "&&", supports "cd <dir>" segments,
       runs every other segment with subprocess.run(shell=True, check=True)
       inside self.project_path
    3. _create_guidance()        -> writes self.readme to
       <project_path>/<project_name>/guidance.txt

---------------------------------------------------------------------------
WHAT YOU MUST OVERRIDE (all are @property, all return a value)
---------------------------------------------------------------------------

    requirements  -> dict[str, dict[str, str]]
        Input form description. See schema below.
        Value is read by _validate_requirements() and by the view.

    readme        -> str
        Free text written to guidance.txt after creation.

    command       -> str
        Shell command to run. Separate several steps with " && ".
        Use "cd <name> && ..." as the first step to run inside the new
        project directory. Read answers from self.user_input.

Optional (already implemented in _base.py, override only if needed):

    _do_execute() -> None
        Override only when the default split-and-run behaviour is not enough.

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
      because _create_guidance() and the template copy use it.
    - "required": True keys must have no "default" guarantee — they fail
      validation only when missing from self.user_input.
    - "name" is what appears in: ValueError("Missing required inputs: ...")
"""

from ._base import CreateProjectByCommand as Cmd
from typing import override

class Pattern(Cmd):
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
    def command(self):
        name = self.user_input.get("project_name", "")
        return f"some-cli new {name}"