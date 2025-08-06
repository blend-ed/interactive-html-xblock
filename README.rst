InteractiveJSBlock
================

A custom Open edX XBlock for creating interactive HTML/CSS/JS content with learner interaction tracking.

This XBlock allows course authors to define custom HTML, CSS, and JavaScript content and automatically captures learner interactions in JSON format for analytics, grading, or state restoration.

Features
--------

* **Custom HTML/CSS/JS Content**: Authors can define their own HTML, CSS, and JavaScript content
* **Learner Interaction Tracking**: Automatically captures learner interactions in JSON format
* **Auto-Grading Support**: Optional automatic grading based on interaction data
* **Debug Mode**: Built-in debug panel for development and testing
* **Studio Editor**: Tabbed interface for easy content editing
* **Preview Functionality**: Live preview of content in studio
* **Responsive Design**: Works on desktop and mobile devices

Installation
-----------

System Administrator
~~~~~~~~~~~~~~~~~~~

To install the XBlock on your platform, add the following to your ``OPENEDX_EXTRA_PIP_REQUIREMENTS``:

  git+https://github.com/openedx/interactive-html-xblock.git@main


Course Staff
~~~~~~~~~~~~

To install the XBlock in your course, access your ``Advanced Module List``:

    Settings -> Advanced Settings -> Advanced Module List

and add the following:

    interactive_js_block

Usage
-----

Studio View (Authoring)
~~~~~~~~~~~~~~~~~~~~~~

1. Add the InteractiveJSBlock to your course
2. Click "Edit" to open the studio editor
3. Update the following fields:
   - **HTML Content**: The structure and content of your interactive element
   - **CSS Styles**: Styling for your content (scoped to the block)
   - **Settings**: Configuration options

4. Use the ``submitInteraction(data)`` function in your JavaScript to capture learner interactions:

   .. code-block:: javascript

       function submitAnswer(answer) {
         submitInteraction({
           answer: answer,
           question: "What is 2 + 2?",
           correct: answer === "4",
           timeSpent: Date.now() - startTime
         });
       }

LMS View (Learner Interaction)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Learners will see the rendered HTML content with the author's CSS and JavaScript applied. The XBlock automatically provides the ``submitInteraction()`` function for capturing interactions.

Configuration Options
-------------------

* **Display Name**: The title shown to learners
* **Weight**: Points value for grading purposes
* **Enable Debug Mode**: Show debug information and console logs
* **Enable Auto-Grading**: Automatically grade based on interaction data
* **Allowed External URLs**: Optional list of allowed external CSS/JS URLs

Auto-Grading
------------

When auto-grading is enabled, the XBlock will automatically assign scores based on interaction data containing:

* ``score``: Direct score value
* ``grade``: Grade value (0-1)
* ``correct``: Boolean indicating correctness

Example:

.. code-block:: javascript

    submitInteraction({
      answer: "B",
      correct: true,
      timeSpent: 45
    });

Development with Tutor
~~~~~~~~~~~~~~~~~~~~~

To develop this xblock with Tutor:

1. Clone the xblock repository
2. Navigate to the folder and install in development mode:

   .. code-block:: bash

       cd interactive-html-xblock
       pip install -e .

3. Add this folder to Tutor mounts:

   .. code-block:: bash

       tutor mounts add /path/to/interactive-html-xblock

4. Create a new tutor plugin to add additional mounting configuration (touch $(tutor plugins printroot)/mount_interactive_html_xblock.py):

   .. code-block:: python

       from tutor import hooks

       hooks.Filters.MOUNTED_DIRECTORIES.add_item(("openedx", "interactive_html_xblock"))

5. Enable the plugin:

   .. code-block:: bash

       tutor plugins enable mount_interactive_html_xblock

6. Build the development image:

   .. code-block:: bash

       tutor images build openedx-dev

6. Start the development environment:

   .. code-block:: bash

       tutor dev start -d

Workbench Scenarios
------------------

The XBlock includes several workbench scenarios for testing:

* Basic InteractiveJSBlock
* Multiple InteractiveJSBlock instances
* InteractiveJSBlock with custom quiz content

Example Quiz Implementation
--------------------------

.. code-block:: html

    <div class="quiz-container">
      <h2>Interactive Quiz</h2>
      <div class="question">
        <p>What is 2 + 2?</p>
        <button onclick="submitAnswer('4')">4</button>
        <button onclick="submitAnswer('5')">5</button>
      </div>
    </div>

.. code-block:: css

    .quiz-container {
      padding: 20px;
      border: 2px solid #007bff;
      border-radius: 8px;
      background: #f8f9fa;
    }
    .question button {
      margin: 5px;
      padding: 10px 20px;
      border: 1px solid #007bff;
      border-radius: 4px;
      background: white;
      cursor: pointer;
    }
    .question button:hover {
      background: #007bff;
      color: white;
    }

.. code-block:: javascript

    function submitAnswer(answer) {
      submitInteraction({
        answer: answer,
        question: "What is 2 + 2?",
        correct: answer === "4",
        timeSpent: Date.now() - startTime
      });
    }
    var startTime = Date.now();
