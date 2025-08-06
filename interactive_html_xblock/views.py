"""
Handle view logic for the InteractiveJSBlock
"""
import json
import datetime
import logging
from xblock.core import XBlock
from xblock.validation import ValidationMessage
from xblock.exceptions import JsonHandlerError
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

        # Create fragment
        fragment = self.build_fragment(
            template=template,
            context=context,
            css=['static/css/interactive_js_block.css'],
            js=['static/js/src/interactive_js_block.js'],
            js_init=self.static_js_init,
        )

        return fragment

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

        # Create fragment
        fragment = self.build_fragment(
            template=template,
            context=context,
            css=['static/css/studio_view.css'],
            js=['static/js/src/studio_view.js'],
            js_init='StudioView',
        )

        return fragment

    def build_fragment(self, template='', context=None, css=None, js=None, js_init=None):
        """
        Creates a fragment for display.
        """
        context = context or {}
        css = css or []
        js = js or []
        
        from web_fragments.fragment import Fragment
        fragment = Fragment(template)
        
        # Add CSS
        for item in css:
            try:
                if item.startswith('/'):
                    fragment.add_css_url(item)
                else:
                    data = self.loader.load_unicode(item)
                    fragment.add_css(data)
            except Exception as e:
                log.error("Error loading CSS file %s: %s", item, str(e))
        
        # Add JavaScript
        for item in js:
            try:
                url = self.runtime.local_resource_url(self, item)
                fragment.add_javascript_url(url)
            except Exception as e:
                log.error("Error loading JavaScript file %s: %s", item, str(e))
        
        if js_init:
            fragment.initialize_js(js_init)
        
        return fragment

    def _i18n_service(self):
        """
        Provide the XBlock runtime's i18n service
        """
        service = self.runtime.service(self, 'i18n')
        return service

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
            i18n_service=self._i18n_service(),
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
        # Validate HTML content
        if 'html_content' in data and not data['html_content'].strip():
            validation.add(
                ValidationMessage(
                    ValidationMessage.ERROR,
                    'HTML content cannot be empty'
                )
            )
        
        # Validate weight
        if 'weight' in data:
            try:
                weight = int(data['weight'])
                if weight < 0:
                    validation.add(
                        ValidationMessage(
                            ValidationMessage.ERROR,
                            'Weight must be a non-negative integer'
                        )
                    )
            except ValueError:
                validation.add(
                    ValidationMessage(
                        ValidationMessage.ERROR,
                        'Weight must be a valid integer'
                    )
                )
        
        # Validate external URLs
        if 'allowed_external_urls' in data:
            try:
                urls = json.loads(data['allowed_external_urls'])
                if not isinstance(urls, list):
                    validation.add(
                        ValidationMessage(
                            ValidationMessage.ERROR,
                            'Allowed external URLs must be a JSON array'
                        )
                    )
            except json.JSONDecodeError:
                validation.add(
                    ValidationMessage(
                        ValidationMessage.ERROR,
                        'Allowed external URLs must be valid JSON'
                    )
                ) 