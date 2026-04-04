"""
Handle view logic for the InteractiveJSBlock
"""
import json
import datetime
import logging
from xblock.core import XBlock
from web_fragments.fragment import Fragment
try:
    # Older Open edX releases (Redwood and earlier) install a backported version of
    # importlib.resources: https://pypi.org/project/importlib-resources/
    import importlib_resources
except ModuleNotFoundError:
    # Starting with Sumac, Open edX drops importlib-resources in favor of the standard library:
    # https://docs.python.org/3/library/importlib.resources.html#module-importlib.resources
    from importlib import resources as importlib_resources
try:
    from xblock.utils.resources import ResourceLoader
    from xblock.utils.studio_editable import StudioEditableXBlockMixin
except ModuleNotFoundError:  # pragma: no cover
    from xblockutils.resources import ResourceLoader
    from xblockutils.studio_editable import StudioEditableXBlockMixin

# Initialize logger
log = logging.getLogger(__name__)


class InteractiveJSBlockViewMixin(StudioEditableXBlockMixin):
    """
    Handle view logic for InteractiveJSBlock instances
    """

    loader = ResourceLoader(__name__)
    static_js_init = 'InteractiveJSBlockView'

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        try:
            data = importlib_resources.files(__name__).joinpath(path).read_bytes()
        except TypeError:
            data = importlib_resources.files(__package__).joinpath(path).read_bytes()
        return data.decode("utf8")

    # Define editable fields for StudioEditableXBlockMixin
    editable_fields = [
        'display_name',
        'html_content',
        'css_content',
        'js_content',
        'enable_debug_mode',
        'auto_grade_enabled',
        'weight',
        'correct_answers',
        'show_feedback_to_learners',
        'show_previous_response',
    ]

    def get_editable_fields(self):
        """
        Return the list of editable fields for StudioEditableXBlockMixin
        """
        return self.editable_fields

    def get_editable_fields_names(self):
        """
        Return the list of editable field names for StudioEditableXBlockMixin
        """
        return self.editable_fields

    def student_view(self, context=None):
        """
        The primary view of the InteractiveJSBlock, shown to students
        within the LMS.
        """
        if context is None:
            context = {}

        # Get user information via user service
        user_service = self.runtime.service(self, 'user')
        user = user_service.get_current_user() if user_service else None
        user_id = user.opt_attrs.get('edx-platform.user_id') if user else None
        username = user.opt_attrs.get('edx-platform.username') if user else None

        # Prepare context
        context.update({
            'block_id': str(self.location),
            'display_name': self.display_name,
            'html_content': self.html_content,
            'css_content': self.css_content,
            'js_content': self.js_content,
            'enable_debug_mode': self.enable_debug_mode,
            'show_feedback_to_learners': self.show_feedback_to_learners,
            'show_previous_response': self.show_previous_response,
            'weight': self.weight,

            # Learner state
            'learner_response': self.learner_response,
            'interaction_count': self.interaction_count,
            'last_interaction_time': self.last_interaction_time,
            'is_correct': self.is_correct,
            'score': self.score,
            'feedback_message': self.feedback_message,

            # User information
            'user_id': user_id,
            'username': username,

            # Staff information
            'is_staff': self.is_staff(),
        })

        # Render the template
        template = self.render_template('static/html/student_view.html', context)

        # Create fragment
        frag = Fragment(template)
        frag.add_css(self.resource_string("static/css/interactive_js_block.css"))
        frag.add_javascript(self.resource_string("public/js/interactive_js_block.js"))
        frag.initialize_js('InteractiveJSBlockView')

        return frag

    def studio_view(self, context=None):
        """
        Create the studio view for editing the InteractiveJSBlock
        """
        context = context or {}
        context = dict(context)

        # Prepare the context for studio editing
        context.update({
            'block_id': str(self.location),
            'display_name': self.display_name,
            'html_content': self.html_content,
            'css_content': self.css_content,
            'js_content': self.js_content,
            'enable_debug_mode': self.enable_debug_mode,
            'auto_grade_enabled': self.auto_grade_enabled,
            'weight': self.weight,
            'correct_answers': json.dumps(self.correct_answers),
            'show_feedback_to_learners': self.show_feedback_to_learners,
            'show_previous_response': self.show_previous_response,
        })

        # Load the studio template
        template = self.render_template('static/html/studio_view.html', context)

        # Create fragment
        frag = Fragment(template)
        frag.add_javascript(self.resource_string("public/js/studio_view.js"))
        frag.initialize_js('StudioView')

        return frag

    def render_template(self, template_path, context):
        """
        Render a template with the given context. The template is translated
        according to the user's language.

        Args:
            template_path (str): The path to the template
            context(dict, optional): The context to render in the template

        Returns:
            str: The rendered template
        """
        return self.loader.render_django_template(
            template_path,
            context,
            i18n_service=self.runtime.service(self, 'i18n'),
        )

    def _evaluate_response(self, data):
        """
        Evaluate the learner response and determine if it's correct.
        """
        # If author's JavaScript provides a 'correct' field, use it directly
        if 'correct' in data and isinstance(data['correct'], bool):
            is_correct = data['correct']
            score = self.weight if is_correct else 0.0
            feedback = data.get('feedback', '') or (
                self.correct_answers.get('correct_feedback', 'Correct!') if is_correct
                else self.correct_answers.get('incorrect_feedback', 'Incorrect. Try again.')
            )
            return is_correct, score, feedback

        # If auto-grading is not enabled or no correct answers configured, return defaults
        if not self.auto_grade_enabled or not self.correct_answers:
            return False, 0.0, ""

        try:
            is_correct = False
            score = 0.0
            feedback = ""

            # Simple evaluation - check if answer field matches
            if 'answer' in data and 'answer' in self.correct_answers:
                user_answer = str(data['answer']).strip().lower()
                correct_answer = str(self.correct_answers['answer']).strip().lower()
                is_correct = user_answer == correct_answer

                if is_correct:
                    score = self.weight
                    feedback = self.correct_answers.get('correct_feedback', 'Correct!')
                else:
                    feedback = self.correct_answers.get('incorrect_feedback', 'Incorrect. Try again.')

            # Multi-field evaluation
            elif 'fields' in self.correct_answers:
                total_fields = len(self.correct_answers['fields'])
                correct_fields = 0

                for field_name, expected_value in self.correct_answers['fields'].items():
                    if field_name in data:
                        user_value = str(data[field_name]).strip().lower()
                        expected = str(expected_value).strip().lower()
                        if user_value == expected:
                            correct_fields += 1

                is_correct = correct_fields == total_fields
                score = (correct_fields / total_fields) * self.weight if total_fields > 0 else 0.0

                if is_correct:
                    feedback = self.correct_answers.get('correct_feedback', 'All answers correct!')
                else:
                    feedback = self.correct_answers.get(
                        'incorrect_feedback',
                        f'{correct_fields}/{total_fields} answers correct.'
                    )

            return is_correct, score, feedback

        except (KeyError, TypeError, ValueError) as e:
            log.exception("Error evaluating response")
            return False, 0.0, "Error evaluating response"

    @XBlock.json_handler
    def save_interaction(self, data, suffix=''):
        """
        Save learner interaction data from JavaScript.
        """
        # Validate that data is provided
        if not data:
            return {'status': 'error', 'message': 'No data provided'}

        if not isinstance(data, dict):
            return {'status': 'error', 'message': 'Data must be a JSON object'}

        # Evaluate the response
        is_correct, score, feedback = self._evaluate_response(data)

        # Update learner state
        self.learner_response = data
        self.interaction_count += 1
        self.last_interaction_time = datetime.datetime.utcnow().isoformat()
        self.is_correct = is_correct
        self.score = score
        self.feedback_message = feedback

        # Publish grade if auto-grading is enabled
        if self.auto_grade_enabled:
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
                log.exception("Could not publish grade")

        # Emit completion
        try:
            self.emit_completion(1.0)
        except Exception:
            log.exception("Could not emit completion")

        return {
            'status': 'ok',
            'message': 'Interaction saved successfully',
            'interaction_count': self.interaction_count,
            'is_correct': self.is_correct,
            'score': self.score,
            'weight': self.weight,
            'feedback_message': self.feedback_message,
            'show_feedback': self.show_feedback_to_learners,
        }

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Handle studio form submission for saving block settings.
        Access control is handled by Studio itself — only users with
        course edit permissions can reach this handler.
        """

        # Update block fields
        self.display_name = data.get('display_name', 'Interactive JS Block')
        self.html_content = data.get('html_content', '')
        self.css_content = data.get('css_content', '')
        self.js_content = data.get('js_content', '')
        self.weight = int(data.get('weight', 1))
        self.enable_debug_mode = data.get('enable_debug_mode', False)
        self.auto_grade_enabled = data.get('auto_grade_enabled', False)
        self.show_feedback_to_learners = data.get('show_feedback_to_learners', True)
        self.show_previous_response = data.get('show_previous_response', True)

        # Handle correct_answers
        correct_answers = data.get('correct_answers', {})
        if isinstance(correct_answers, str):
            try:
                self.correct_answers = json.loads(correct_answers)
            except json.JSONDecodeError:
                self.correct_answers = {}
        else:
            self.correct_answers = correct_answers

        # Validate required fields
        if not self.html_content.strip():
            return {'result': 'error', 'message': 'HTML content cannot be empty'}

        log.info("Studio settings saved successfully for block %s", str(self.location))

        return {'result': 'success'}
