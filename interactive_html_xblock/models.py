"""
Handle data access logic for the InteractiveJSBlock
"""
from django.utils.translation import gettext_lazy as _
from xblock.fields import Boolean, JSONField, List, Scope, String, Integer


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

    # XBlock configuration
    has_score = True
    show_in_read_only_mode = True

    def get_allowed_external_urls(self):
        """
        Ensure allowed_external_urls is always a list
        """
        urls = getattr(self, 'allowed_external_urls', None)
        if urls is None:
            return []
        if not isinstance(urls, list):
            return []
        return urls

    def ensure_field_initialization(self):
        """
        Ensure all fields are properly initialized
        """
        if not hasattr(self, 'allowed_external_urls') or self.allowed_external_urls is None:
            self.allowed_external_urls = []
        if not hasattr(self, 'learner_response') or self.learner_response is None:
            self.learner_response = {}
        if not hasattr(self, 'interaction_count') or self.interaction_count is None:
            self.interaction_count = 0
        if not hasattr(self, 'last_interaction_time') or self.last_interaction_time is None:
            self.last_interaction_time = ''

    def max_score(self):
        """
        Returns the configured number of possible points for this component.
        """
        return self.weight

    def get_score(self):
        """
        Get the current score for this XBlock.
        """
        if hasattr(self, 'score'):
            return self.score
        return 0.0

    def set_score(self, score):
        """
        Set the score for this XBlock.
        """
        self.score = score
        try:
            self.runtime.publish(
                self,
                'grade',
                {
                    'value': self.score,
                    'max_value': self.max_score()
                }
            )
        except Exception:
            pass  # Handle gracefully if runtime doesn't support publishing 