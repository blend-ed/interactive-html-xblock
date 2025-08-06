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
        Create the student view of the InteractiveJSBlock
        """
        # Ensure all fields are properly initialized
        self.ensure_field_initialization()
        
        context = context or {}
        context = dict(context)
        
        # Prepare the context for rendering
        context.update({
            'block_id': str(self.location),
            'display_name': getattr(self, 'display_name', 'Interactive JS Block'),
            'html_content': getattr(self, 'html_content', ''),
            'css_content': getattr(self, 'css_content', ''),
            'js_content': getattr(self, 'js_content', ''),
            'allowed_external_urls': self.get_allowed_external_urls(),
            'enable_debug_mode': getattr(self, 'enable_debug_mode', False),
            'learner_response': getattr(self, 'learner_response', {}),
            'interaction_count': getattr(self, 'interaction_count', 0),
            'last_interaction_time': getattr(self, 'last_interaction_time', ''),
        })

        # Load the template
        try:
            template = self.render_template('static/html/student_view.html', context)
        except Exception as e:
            log.error("Error rendering student view template: %s", str(e))
            template = "<div class='xblock-error'>Error loading content</div>"

        # Create fragment using h5pxblock pattern
        frag = Fragment(template)
        frag.add_css(self.resource_string("static/css/interactive_js_block.css"))
        frag.add_javascript(self.resource_string("public/js/interactive_js_block.js"))
        frag.initialize_js(self.static_js_init)
        
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
            # Update learner response
            self.learner_response = data
            self.interaction_count += 1
            self.last_interaction_time = datetime.datetime.utcnow().isoformat()
            
            # Handle auto-grading if enabled
            if self.auto_grade_enabled:
                self._handle_auto_grading(data)
            
            log.info("Interaction saved successfully for user %s", getattr(self.runtime, 'user_id', 'unknown'))
            
            return {
                'status': 'ok',
                'message': 'Interaction saved successfully',
                'interaction_count': self.interaction_count
            }
        except Exception as e:
            log.error("Error saving interaction data: %s", str(e))
            return {
                'status': 'error',
                'message': 'Failed to save interaction'
            }

    def _handle_auto_grading(self, data):
        """
        Handle automatic grading based on interaction data
        """
        # Check if the data contains a score or grade
        try:
            if 'score' in data:
                score = float(data['score'])
                if score < 0 or score > self.max_score():
                    log.warning("Invalid score value: %s (max: %s)", score, self.max_score())
                    return
                self.set_score(score)
            elif 'grade' in data:
                grade = float(data['grade'])
                if grade < 0 or grade > self.max_score():
                    log.warning("Invalid grade value: %s (max: %s)", grade, self.max_score())
                    return
                self.set_score(grade)
            elif 'correct' in data:
                # Boolean grading
                if not isinstance(data['correct'], bool):
                    log.warning("'correct' field must be boolean, got: %s", type(data['correct']))
                    return
                score = self.max_score() if data['correct'] else 0.0
                self.set_score(score)
        except (ValueError, TypeError) as e:
            log.error("Error processing grading data: %s", str(e))

    def validate_field_data(self, validation, data):
        """
        Validate field data in studio
        """
        # The 'data' parameter is actually the XBlock instance (self)
        # We need to validate the current field values
        
        # Validate HTML content
        html_content = getattr(data, 'html_content', '')
        if not html_content or not html_content.strip():
            validation.add(
                ValidationMessage(
                    ValidationMessage.ERROR,
                    'HTML content cannot be empty'
                )
            )
        
        # Validate weight
        weight = getattr(data, 'weight', 1)
        try:
            weight_int = int(weight)
            if weight_int < 0:
                validation.add(
                    ValidationMessage(
                        ValidationMessage.ERROR,
                        'Weight must be a non-negative integer'
                    )
                )
        except (ValueError, TypeError):
            validation.add(
                ValidationMessage(
                    ValidationMessage.ERROR,
                    'Weight must be a valid integer'
                )
            )
        
        # Validate external URLs
        allowed_urls = getattr(data, 'allowed_external_urls', [])
        if allowed_urls is not None:
            if not isinstance(allowed_urls, list):
                validation.add(
                    ValidationMessage(
                        ValidationMessage.ERROR,
                        'Allowed external URLs must be a list'
                    )
                )
            else:
                # Validate each URL
                for url in allowed_urls:
                    if not isinstance(url, str) or not url.strip():
                        validation.add(
                            ValidationMessage(
                                ValidationMessage.ERROR,
                                'All URLs must be non-empty strings'
                            )
                        )
                        break

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