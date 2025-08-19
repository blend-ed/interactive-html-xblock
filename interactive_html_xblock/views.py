"""
Handle view logic for the InteractiveJSBlock
"""
import json
import datetime
import logging
from xblock.core import XBlock
from xblock.validation import ValidationMessage
from xblock.exceptions import JsonHandlerError
from web_fragments.fragment import Fragment
from webob import Response
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

from .models import InteractiveJSBlockModelMixin

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
        'allowed_external_urls',
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

        # Get user information
        user = self.runtime.get_real_user(self.runtime.anonymous_student_id)
        user_id = user.id if user else None
        username = user.username if user else None
        user_email = user.email if user else None
        user_full_name = user.get_full_name() if user else None

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
            'user_email': user_email,
            'user_full_name': user_full_name,
            
            # Staff information
            'is_staff': self.is_staff(),
        })

        # Render the template
        template = self._render_template('static/html/student_view.html', context)
        
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
        # Ensure all fields are properly initialized
        self.ensure_field_initialization()
        
        context = context or {}
        context = dict(context)
        
        # Prepare the context for studio editing
        context.update({
            'block_id': str(self.location),
            'display_name': getattr(self, 'display_name', 'Interactive JS Block'),
            'html_content': getattr(self, 'html_content', ''),
            'css_content': getattr(self, 'css_content', ''),
            'js_content': getattr(self, 'js_content', ''),
            'allowed_external_urls': json.dumps(self.get_allowed_external_urls()),
            'enable_debug_mode': getattr(self, 'enable_debug_mode', False),
            'auto_grade_enabled': getattr(self, 'auto_grade_enabled', False),
            'weight': getattr(self, 'weight', 1),
            'correct_answers': json.dumps(getattr(self, 'correct_answers', {})),
            'show_feedback_to_learners': getattr(self, 'show_feedback_to_learners', True),
            'show_previous_response': getattr(self, 'show_previous_response', True),

        })

        # Load the studio template
        try:
            template = self.render_template('static/html/studio_view.html', context)
        except Exception as e:
            log.error("Error rendering studio view template: %s", str(e))
            template = "<div class='xblock-error'>Error loading studio view</div>"

        # Create fragment using h5pxblock pattern
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

    def _render_template(self, template_path, context):
        """
        Helper to render a template with the given context.
        """
        return self.loader.render_django_template(
            template_path,
            context,
            i18n_service=self.runtime.service(self, 'i18n'),
        )

    def _evaluate_response(self, data):
        """
        Evaluate the learner response and determine if it's correct
        """
        correct_answers = getattr(self, 'correct_answers', {})
        auto_grade_enabled = getattr(self, 'auto_grade_enabled', False)
        
        log.info("Evaluating response: data=%s, correct_answers=%s, auto_grade_enabled=%s", 
                data, correct_answers, auto_grade_enabled)
        
        # If author's JavaScript provides a 'correct' field, use it directly
        if 'correct' in data and isinstance(data['correct'], bool):
            is_correct = data['correct']
            score = self.weight if is_correct else 0.0
            feedback = data.get('feedback', '') or (
                correct_answers.get('correct_feedback', 'Correct!') if is_correct 
                else correct_answers.get('incorrect_feedback', 'Incorrect. Try again.')
            )
            log.info("Using author-provided correct field: is_correct=%s, score=%s, feedback=%s", 
                    is_correct, score, feedback)
            return is_correct, score, feedback
        
        # If auto-grading is not enabled, return default values
        if not auto_grade_enabled or not correct_answers:
            log.info("Auto-grading not enabled or no correct answers configured")
            return False, 0.0, ""
        
        try:
            # Check if the response matches any correct answer
            is_correct = False
            score = 0.0
            feedback = ""
            
            # Simple evaluation - check if answer field matches
            if 'answer' in data and 'answer' in correct_answers:
                user_answer = str(data['answer']).strip().lower()
                correct_answer = str(correct_answers['answer']).strip().lower()
                is_correct = user_answer == correct_answer
                
                if is_correct:
                    score = self.weight
                    feedback = correct_answers.get('correct_feedback', 'Correct!')
                else:
                    feedback = correct_answers.get('incorrect_feedback', 'Incorrect. Try again.')
                
                log.info("Simple evaluation: user_answer='%s', correct_answer='%s', is_correct=%s, score=%s", 
                        user_answer, correct_answer, is_correct, score)
            
            # More complex evaluation for multiple fields
            elif 'fields' in correct_answers:
                total_fields = len(correct_answers['fields'])
                correct_fields = 0
                
                for field_name, expected_value in correct_answers['fields'].items():
                    if field_name in data:
                        user_value = str(data[field_name]).strip().lower()
                        expected_value = str(expected_value).strip().lower()
                        if user_value == expected_value:
                            correct_fields += 1
                
                is_correct = correct_fields == total_fields
                score = (correct_fields / total_fields) * self.weight if total_fields > 0 else 0.0
                
                if is_correct:
                    feedback = correct_answers.get('correct_feedback', 'All answers correct!')
                else:
                    feedback = correct_answers.get('incorrect_feedback', f'{correct_fields}/{total_fields} answers correct.')
                
                log.info("Complex evaluation: correct_fields=%s, total_fields=%s, is_correct=%s, score=%s", 
                        correct_fields, total_fields, is_correct, score)
            
            return is_correct, score, feedback
            
        except Exception as e:
            log.error("Error evaluating response: %s", str(e))
            return False, 0.0, "Error evaluating response"

    @XBlock.json_handler
    def save_interaction(self, data, suffix=''):
        """
        Save learner interaction data from JavaScript
        """
        # Validate that data is provided
        if not data:
            log.warning("save_interaction called with no data provided")
            return {'status': 'error', 'message': 'No data provided'}
            
        if not isinstance(data, dict):
            log.warning("save_interaction called with invalid data type: %s", type(data))
            return {'status': 'error', 'message': 'Data must be a JSON object'}
        
        try:
            # Evaluate the response if auto-grading is enabled
            is_correct, score, feedback = self._evaluate_response(data)
            
            # Update learner response
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
                except Exception as e:
                    log.warning("Could not publish grade: %s", str(e))
            
            log.info("Interaction saved successfully for user %s", getattr(self.runtime, 'user_id', 'unknown'))
            
            response_data = {
                'status': 'ok',
                'message': 'Interaction saved successfully',
                'interaction_count': self.interaction_count,
                'is_correct': self.is_correct,
                'score': self.score,
                'weight': self.weight,
                'feedback_message': self.feedback_message,
                'show_feedback': self.show_feedback_to_learners
            }
            
            log.info("Returning response data: %s", response_data)
            return response_data
            
        except Exception as e:
            log.error("Error saving interaction: %s", str(e))
            return {'status': 'error', 'message': 'Failed to save interaction'}

    @XBlock.json_handler
    def get_learner_data(self, data, suffix=''):
        """
        Get learner data for staff view
        """
        if not self.is_staff():
            return {'status': 'error', 'message': 'Access denied'}
        
        try:
            return {
                'status': 'ok',
                'learner_response': self.learner_response,
                'interaction_count': self.interaction_count,
                'last_interaction_time': self.last_interaction_time,
                'is_correct': self.is_correct,
                'score': self.score,
                'feedback_message': self.feedback_message,
            }
        except Exception as e:
            log.error("Error getting learner data: %s", str(e))
            return {'status': 'error', 'message': 'Failed to get learner data'}







    @XBlock.handler
    def export_submissions(self, request, suffix=""):
        """
        Export submission history as CSV for instructors
        """
        if not self.is_staff():
            return Response(
                json.dumps({"error": "Access denied"}),
                content_type="application/json",
                charset="utf8"
            )
        
        try:
            import csv
            import io
            from datetime import datetime
            
            # Create CSV data
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Student Name',
                'Username', 
                'Email',
                'Answer',
                'Score',
                'Correct',
                'Feedback Message',
                'Interaction Count',
                'Last Submission Time',
                'Full Response Data'
            ])
            
            # Get current user info
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=request.user.id)
                full_name = user.get_full_name() or user.username
            except:
                full_name = "Unknown"
            
            # Write data row
            answer = self.learner_response.get('answer', '') if self.learner_response else ''
            writer.writerow([
                full_name,
                request.user.username,
                request.user.email,
                answer,
                self.score,
                'Yes' if self.is_correct else 'No',
                self.feedback_message,
                self.interaction_count,
                self.last_interaction_time,
                json.dumps(self.learner_response) if self.learner_response else ''
            ])
            
            # Prepare response
            csv_data = output.getvalue()
            output.close()
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"interactive_js_submissions_{self.location.block_id}_{timestamp}.csv"
            
            response = Response(
                csv_data,
                content_type="text/csv",
                charset="utf8"
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            log.error("Error exporting submissions: %s", str(e))
            return Response(
                json.dumps({"error": "Failed to export submissions"}),
                content_type="application/json",
                charset="utf8"
            )

    @XBlock.handler
    def studio_submit(self, request, suffix=""):
        """
        Handle studio form submission for saving block settings
        """
        try:
            # Parse the JSON data from the request
            data = json.loads(request.body.decode('utf-8'))
            
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
            
            # Handle allowed_external_urls
            allowed_urls = data.get('allowed_external_urls', [])
            if isinstance(allowed_urls, list):
                self.allowed_external_urls = allowed_urls
            else:
                self.allowed_external_urls = []
            
            # Validate required fields
            if not self.html_content.strip():
                return Response(
                    json.dumps({"result": "error", "message": "HTML content cannot be empty"}),
                    content_type="application/json",
                    charset="utf8"
                )
            
            log.info("Studio settings saved successfully for block %s", str(self.location))
            
            return Response(
                json.dumps({"result": "success"}),
                content_type="application/json",
                charset="utf8"
            )
            
        except json.JSONDecodeError as e:
            log.error("Invalid JSON in studio submit: %s", str(e))
            return Response(
                json.dumps({"result": "error", "message": "Invalid data format"}),
                content_type="application/json",
                charset="utf8"
            )
        except Exception as e:
            log.error("Error saving studio settings: %s", str(e))
            return Response(
                json.dumps({"result": "error", "message": "Failed to save settings"}),
                content_type="application/json",
                charset="utf8"
            ) 