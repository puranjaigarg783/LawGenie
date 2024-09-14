<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [LawGenie](#lawgenie)
  - [Package Management](#package-management)
  - [Pre-commit Hooks](#pre-commit-hooks)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# LawGenie


## Package Management

`pip install uv` to install the package manager, then `uv run <command>` to run any command inside the virtual environment for this project. `uv` will take care of the requirements installation.

`uv add <package>`/`uv remove <package>` to add or remove requirements.

## Pre-commit Hooks

This repo has some pre-commit hooks set up that take care of common tasks like linting, formatting, checking for trailing whitespaces, etc. To enable this feature (only useful while developing), first run (preceded by `uv run`, like all commands) `pre-commit install`. (i.e., `uv run pre-commit install`) This will enable the pre-commit hooks in your git config for this project. The pre-commit hooks in the pre-commit-config yaml file should now run before each commit. This will make sure your files are formatted correctly. Sometimes, this gives a warning, so your commit doesn't go through, but the issues are fixed. (this might especially happen in case you change the readme since one of the hooks makes an automatic content section for the readme) In this case, just try to commit again and it should work. The only time you'll have to worry about these pre-commit hooks is when they show you that some file failed the pre-commit check. In that case, just fix the issue with the file!

You can also manually run all the checks without commiting with `uv run pre-commit run --all-files`
