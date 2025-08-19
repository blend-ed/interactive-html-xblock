"""
Handle data access logic for the InteractiveJSBlock
"""
from django.utils.translation import gettext_lazy as _
from xblock.fields import Boolean, JSONField, List, Scope, String, Integer, Float


class InteractiveJSBlockModelMixin(object):
    """
    Handle data access for InteractiveJSBlock instances
    """

    # Author content fields
    html_content = String(
        display_name=_('HTML Content'),
        help=_('HTML content to render in the interactive block'),
        default='<div class="interactive-content">\n  <h3>Interactive Content</h3>\n  <p>Add your interactive HTML here.</p>\n</div>',
        scope=Scope.content,
        multiline_editor=True,
    )

    css_content = String(
        display_name=_('CSS Content'),
        help=_('CSS styles for the interactive content'),
        default='.interactive-content {\n  padding: 20px;\n  border: 1px solid #ccc;\n  border-radius: 5px;\n}',
        scope=Scope.content,
        multiline_editor=True,
    )

    js_content = String(
        display_name=_('JavaScript Content'),
        help=_('JavaScript code for interactivity. Use submitInteraction(data) to send data to the XBlock.'),
        default='// Example: submitInteraction({ answer: "user input", timeSpent: 30 });\nconsole.log("Interactive JS loaded");',
        scope=Scope.content,
        multiline_editor=True,
    )

    allowed_external_urls = List(
        display_name=_('Allowed External URLs'),
        help=_('List of allowed external CSS/JS URLs (optional)'),
        default=[],
        scope=Scope.content,
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

    def get_allowed_external_urls(self):
        """
        Ensure allowed_external_urls is always a list
        """
        urls = getattr(self, 'allowed_external_urls', [])
        if urls is None:
            return []
        return urls

    def ensure_field_initialization(self):
        """
        Ensure all fields are properly initialized
        """
        # Initialize fields that might be None
        if not hasattr(self, 'learner_response') or self.learner_response is None:
            self.learner_response = {}
        
        if not hasattr(self, 'interaction_count') or self.interaction_count is None:
            self.interaction_count = 0
            
        if not hasattr(self, 'last_interaction_time') or self.last_interaction_time is None:
            self.last_interaction_time = ''
            
        if not hasattr(self, 'is_correct') or self.is_correct is None:
            self.is_correct = False
            
        if not hasattr(self, 'score') or self.score is None:
            self.score = 0.0
            
        if not hasattr(self, 'feedback_message') or self.feedback_message is None:
            self.feedback_message = ''

    def is_staff(self):
        """
        Return True if the current user is staff
        """
        if hasattr(self, "xmodule_runtime") and \
           hasattr(self.xmodule_runtime, "user_is_staff"):
            return self.xmodule_runtime.user_is_staff
        else:
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