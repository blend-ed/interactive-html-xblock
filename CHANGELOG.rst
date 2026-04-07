Change Log
##########

..
   All enhancements and patches to interactive_content_xblock will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
**********

*

1.0.0 – 2026-04-03
*******************

Added
=====

* Interactive HTML/CSS/JS content rendering with ``submitInteraction(data)`` API
* Auto-grading with two modes: author JS-provided ``correct`` field, or server-side answer matching
* Server-side answer matching: single answer and multi-field with partial credit
* Friendly Studio grading form replacing raw JSON textarea (mode selector, text inputs, add/remove rows)
* Test Grading panel in Studio for instant client-side verification of grading config
* Completion tracking via ``CompletableXBlockMixin.emit_completion()``
* Configurable correct/incorrect feedback messages
* Previous response display for returning learners
* Staff debug panel (gated by debug mode setting)
* Masquerade support via ``show_in_read_only_mode = True``
* Default sample quiz (geography question) for new blocks
* Django 4.2 and 5.2 support
* Python 3.11+ support

0.1.0 – 2025-08-05
*******************

Added
=====

* First release on PyPI.
