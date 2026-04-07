# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Open edX XBlock (`interactive-content-xblock`) that lets course authors create interactive HTML/CSS/JS content with learner interaction tracking and auto-grading. The XBlock is registered as `interactive_content_xblock` in the entry points.

## Common Commands

### Install dependencies
```bash
pip install -e .  # development install
make requirements  # full dev environment (pip-sync)
```

### Run tests
```bash
tox -e py312-django52        # run tests with Django 5.2
tox -e py312-django42        # run tests with Django 4.2
pytest tests/test_interactive_content_xblock.py  # run specific test file
pytest tests/test_interactive_content_xblock.py::TestInteractiveContentXBlock::test_method_name  # single test
```

### Quality checks
```bash
tox -e quality  # pylint, pycodestyle, pydocstyle, isort
```

### Compile requirements
```bash
make compile-requirements  # pin current versions
make upgrade               # upgrade all pinned versions
```

### Docker workbench
```bash
make dev.run   # clean, build, and run workbench at localhost:8000
make dev.stop  # stop container
```

### Translations
```bash
make extract_translations
make compile_translations
make validate_translations
```

## Architecture

The XBlock is split into three mixins composed in `InteractiveContentXBlock` (xblocks.py):

- **`InteractiveContentXBlockModelMixin`** (`models.py`) — All XBlock fields (content fields with `Scope.content`, learner state with `Scope.user_state`), scoring logic (`has_score = True`), and staff detection.
- **`InteractiveContentXBlockViewMixin`** (`views.py`) — `student_view`, `studio_view`, JSON handlers (`save_interaction`, `studio_submit`), and response evaluation (`_evaluate_response`).
- **`InteractiveContentXBlock`** (`xblocks.py`) — Composes the mixins with `XBlock` and `CompletableXBlockMixin`. Defines workbench scenarios.

### Frontend

- `public/js/interactive_content_xblock.js` — Student-facing JS, initialized as `InteractiveContentXBlockView`
- `public/js/studio_view.js` — Studio editor JS, initialized as `StudioView`
- `static/html/student_view.html` / `studio_view.html` — Django templates
- `static/css/interactive_content_xblock.css` — Student view styles

### Key interaction flow

1. Author JS calls `submitInteraction(data)` from within the rendered content
2. This triggers the `save_interaction` JSON handler on the backend
3. `_evaluate_response` checks for a `correct` boolean in the data, or compares against `correct_answers` field config
4. If `auto_grade_enabled`, a grade event is published via `runtime.publish`
5. Completion is emitted via `CompletableXBlockMixin.emit_completion(1.0)`

### Staff data access

Staff view individual student data using the platform's built-in masquerading ("View as Specific Learner"), which works because `show_in_read_only_mode = True`. Bulk data exports are handled by the instructor dashboard. The XBlock does NOT attempt to access other users' `Scope.user_state` data.

## Test Configuration

- pytest uses `DJANGO_SETTINGS_MODULE = workbench.settings`
- Coverage targets the `interactive_content_xblock` package
- tox tests against Django 4.2 and 5.2

## Code Style

- Max line length: 120 (pycodestyle)
- Import sorting: isort
- Linting: pylint with custom `pylintrc` and `pylintrc_tweaks`
- Python ≥ 3.11 required

## Development with Tutor

For local Open edX development, mount the xblock directory into Tutor:
```bash
tutor mounts add /path/to/interactive-content-xblock
tutor images build openedx-dev
tutor dev start -d
```
A Tutor plugin is needed to register the mount — see README.rst for details.
