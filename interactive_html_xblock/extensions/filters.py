"""
Open edX Filters needed for instructor dashboard integration.
"""
import importlib.resources
from crum import get_current_request
from django.conf import settings
from django.template import Context, Template
from openedx_filters import PipelineStep
from web_fragments.fragment import Fragment

try:
    from cms.djangoapps.contentstore.utils import get_lms_link_for_item
    from lms.djangoapps.courseware.block_render import (get_block_by_usage_id,
                                                        load_single_xblock)
    from openedx.core.djangoapps.enrollments.data import get_user_enrollments
    from xmodule.modulestore.django import modulestore
except ImportError:
    load_single_xblock = None
    get_block_by_usage_id = None
    modulestore = None
    get_user_enrollments = None
    get_lms_link_for_item = None

TEMPLATE_ABSOLUTE_PATH = "/instructor_dashboard/"
BLOCK_CATEGORY = "interactive_js_block"
TEMPLATE_CATEGORY = "interactive_js_instructor"


class AddInteractiveJSTab(PipelineStep):
    """Add interactive_js_block tab to instructor dashboard by adding a new context with interaction data."""

    def run_filter(
        self, context, template_name
    ):  # pylint: disable=unused-argument, arguments-differ
        """Execute filter that modifies the instructor dashboard context.
        Args:
            context (dict): the context for the instructor dashboard.
            _ (str): instructor dashboard template name.
        """
        if not settings.FEATURES.get("ENABLE_INTERACTIVE_JS_INSTRUCTOR_VIEW", False):
            return {
                "context": context,
            }

        course = context["course"]
        template = Template(
            self.resource_string(f"static/html/{TEMPLATE_CATEGORY}.html")
        )

        request = get_current_request()

        context.update(
            {
                "blocks": load_blocks(request, course),
            }
        )

        html = template.render(Context(context))
        frag = Fragment(html)
        frag.add_css(self.resource_string(f"static/css/{TEMPLATE_CATEGORY}.css"))
        frag.add_javascript(
            self.resource_string(f"static/js/src/{TEMPLATE_CATEGORY}.js")
        )

        section_data = {
            "fragment": frag,
            "section_key": TEMPLATE_CATEGORY,
            "section_display_name": "Interactive JS Blocks",
            "course_id": str(course.id),
            "template_path_prefix": TEMPLATE_ABSOLUTE_PATH,
        }
        context["sections"].append(section_data)

        return {"context": context}

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        return importlib.resources.files("interactive_html_xblock").joinpath(path).read_text(encoding="utf-8")


def load_blocks(request, course):
    """
    Load interactive JS blocks for a given course for all enrolled students.

    Arguments:
        request (HttpRequest): Django request object.
        course (CourseLocator): Course locator object.
    """
    course_id = str(course.id)

    interactive_blocks = modulestore().get_items(
        course.id, qualifiers={"category": BLOCK_CATEGORY}
    )

    blocks = []

    if not interactive_blocks:
        return []

    students = get_user_enrollments(course_id).values_list("user_id", "user__username")
    for interactive_block in interactive_blocks:
        block, _ = get_block_by_usage_id(
            request,
            str(course.id),
            str(interactive_block.location),
            disable_staff_debug_info=True,
            course=course,
        )
        
        if not block.enable_instructor_view:
            continue
            
        interactions = load_xblock_interactions(
            request,
            students,
            str(course.location.course_key),
            str(interactive_block.location),
            course,
        )

        unit = block.get_parent()
        subsection = unit.get_parent()
        section = subsection.get_parent()

        blocks.append(
            {
                "display_name": block.display_name,
                "interactions": interactions,
                "total_interactions": len(interactions),
                "correct_interactions": sum(1 for i in interactions if i.get('is_correct', False)),
                "average_score": sum(i.get('score', 0) for i in interactions) / len(interactions) if interactions else 0,
                "unit_display_name": unit.display_name,
                "subsection_display_name": subsection.display_name,
                "section_display_name": section.display_name,
                "url": get_lms_link_for_item(block.location),
            }
        )
    return blocks


def load_xblock_interactions(request, students, course_id, block_id, course):
    """
    Load interactions for a given interactive JS xblock instance.

    Arguments:
        request (HttpRequest): Django request object.
        students (list): List of enrolled students.
        course_id (str): Course ID.
        block_id (str): Block ID.
        course (CourseDescriptor): Course descriptor.
    """
    interactions = []
    for user_id, username in students:
        student_xblock_instance = load_single_xblock(
            request, user_id, course_id, block_id, course
        )
        if student_xblock_instance and student_xblock_instance.learner_response:
            interactions.append(
                {
                    "username": username,
                    "learner_response": student_xblock_instance.learner_response,
                    "interaction_count": student_xblock_instance.interaction_count,
                    "last_interaction_time": student_xblock_instance.last_interaction_time,
                    "is_correct": student_xblock_instance.is_correct,
                    "score": student_xblock_instance.score,
                    "feedback_message": student_xblock_instance.feedback_message,
                }
            )

    return interactions
