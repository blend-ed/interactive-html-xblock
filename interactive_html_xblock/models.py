"""
Handle data access logic for the InteractiveJSBlock
"""
from django.utils.translation import gettext_lazy as _
from xblock.fields import Boolean, Float, Integer, JSONField, Scope, String


class InteractiveJSBlockModelMixin(object):
    """
    Handle data access for InteractiveJSBlock instances
    """

    # Author content fields
    html_content = String(
        display_name=_('HTML Content'),
        help=_('HTML content to render in the interactive block'),
        default=(
            '<div class="quiz">\n'
            '  <h3>Sample Quiz</h3>\n'
            '  <p>What is the capital of France?</p>\n'
            '  <div class="options">\n'
            '    <button onclick="submitAnswer(\'Paris\')">Paris</button>\n'
            '    <button onclick="submitAnswer(\'London\')">London</button>\n'
            '    <button onclick="submitAnswer(\'Berlin\')">Berlin</button>\n'
            '  </div>\n'
            '  <div id="result"></div>\n'
            '</div>'
        ),
        scope=Scope.content,
        multiline_editor=True,
    )

    css_content = String(
        display_name=_('CSS Content'),
        help=_('CSS styles for the interactive content'),
        default=(
            '.quiz {\n'
            '  padding: 20px;\n'
            '  border: 2px solid #007bff;\n'
            '  border-radius: 8px;\n'
            '  background: #f8f9fa;\n'
            '}\n'
            '.options {\n'
            '  display: flex;\n'
            '  gap: 10px;\n'
            '  margin-top: 12px;\n'
            '}\n'
            '.options button {\n'
            '  padding: 10px 20px;\n'
            '  border: 1px solid #007bff;\n'
            '  border-radius: 4px;\n'
            '  background: white;\n'
            '  cursor: pointer;\n'
            '  font-size: 14px;\n'
            '}\n'
            '.options button:hover {\n'
            '  background: #007bff;\n'
            '  color: white;\n'
            '}'
        ),
        scope=Scope.content,
        multiline_editor=True,
    )

    js_content = String(
        display_name=_('JavaScript Content'),
        help=_('JavaScript code for interactivity. Use submitInteraction(data) to send data to the XBlock.'),
        default=(
            'var startTime = Date.now();\n'
            '\n'
            'function submitAnswer(answer) {\n'
            '  submitInteraction({\n'
            '    answer: answer,\n'
            '    correct: answer === "Paris",\n'
            '    timeSpent: Math.round((Date.now() - startTime) / 1000)\n'
            '  });\n'
            '}'
        ),
        scope=Scope.content,
        multiline_editor=True,
    )

    # Configuration fields
    enable_debug_mode = Boolean(
        display_name=_('Enable Debug Mode'),
        help=_('Show debug information and console logs'),
        default=False,
        scope=Scope.content,
    )

    auto_grade_enabled = Boolean(
        display_name=_('Enable Auto-Grading'),
        help=_('Enable automatic grading based on JS response'),
        default=False,
        scope=Scope.content,
    )

    weight = Integer(
        display_name=_('Weight'),
        help=_('Weight for grading purposes'),
        default=1,
        values={'min': 0},
        scope=Scope.content,
    )

    display_name = String(
        display_name=_('Display Name'),
        help=_('Display name for this interactive block'),
        default='Interactive JS Block',
        scope=Scope.content,
    )

    # New fields for correct answers and feedback
    correct_answers = JSONField(
        display_name=_('Correct Answers'),
        help=_('JSON object defining correct answers for auto-grading'),
        default={},
        scope=Scope.content,
    )

    show_feedback_to_learners = Boolean(
        display_name=_('Show Feedback to Learners'),
        help=_('Show correct/incorrect feedback to learners'),
        default=True,
        scope=Scope.content,
    )

    show_previous_response = Boolean(
        display_name=_('Show Previous Response'),
        help=_('Show learner their previous response when they return'),
        default=True,
        scope=Scope.content,
    )

    # Learner data fields
    learner_response = JSONField(
        help=_('Captured learner interaction data'),
        default={},
        scope=Scope.user_state,
    )

    interaction_count = Integer(
        help=_('Number of interactions submitted'),
        default=0,
        scope=Scope.user_state,
    )

    last_interaction_time = String(
        help=_('Timestamp of last interaction'),
        default='',
        scope=Scope.user_state,
    )

    # New learner state fields
    is_correct = Boolean(
        help=_('Whether the learner response is correct'),
        default=False,
        scope=Scope.user_state,
    )

    score = Float(
        help=_('Score for the learner response'),
        default=0.0,
        scope=Scope.user_state,
    )

    feedback_message = String(
        help=_('Feedback message shown to learner'),
        default='',
        scope=Scope.user_state,
    )

    # XBlock configuration
    has_score = True
    show_in_read_only_mode = True

    def is_staff(self):
        """
        Return True if the current user is staff
        """
        user_service = self.runtime.service(self, 'user')
        if user_service:
            user = user_service.get_current_user()
            if user:
                return user.opt_attrs.get('edx-platform.is_staff', False)
        # In workbench and similar settings, always return true
        return True

    def get_score(self):
        """
        Return the current score
        """
        return self.score

    def max_score(self):
        """
        Return the maximum possible score
        """
        return self.weight 