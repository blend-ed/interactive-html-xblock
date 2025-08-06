"""
This is the core logic for the InteractiveJSBlock
"""
from xblock.core import XBlock
try:
    from xblock.completable import CompletableXBlockMixin
except ImportError:
    # Fallback for older XBlock versions
    class CompletableXBlockMixin:
        pass

from .models import InteractiveJSBlockModelMixin
from .views import InteractiveJSBlockViewMixin


@XBlock.wants('user')
@XBlock.wants('i18n')
class InteractiveJSBlock(
        InteractiveJSBlockModelMixin,
        InteractiveJSBlockViewMixin,
        CompletableXBlockMixin,
        XBlock,
):
    """
    XBlock for creating interactive HTML/CSS/JS content with learner interaction tracking.
    
    This XBlock allows authors to define custom HTML, CSS, and JavaScript content
    and automatically captures learner interactions in JSON format for analytics,
    grading, or state restoration.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the InteractiveJSBlock
        """
        super().__init__(*args, **kwargs)
        # Ensure fields are properly initialized
        if hasattr(self, 'ensure_field_initialization'):
            self.ensure_field_initialization()

    @staticmethod
    def workbench_scenarios():
        """Create canned scenarios for display in the workbench."""
        return [
            ("InteractiveJSBlock",
             """<interactive_js_block/>
             """),
            ("Multiple InteractiveJSBlock",
             """<vertical_demo>
                <interactive_js_block/>
                <interactive_js_block/>
                <interactive_js_block/>
                </vertical_demo>
             """),
            ("InteractiveJSBlock with Custom Content",
             """<interactive_js_block>
                <html_content>
                <div class="quiz-container">
                  <h2>Interactive Quiz</h2>
                  <div class="question">
                    <p>What is 2 + 2?</p>
                    <button onclick="submitAnswer('4')">4</button>
                    <button onclick="submitAnswer('5')">5</button>
                  </div>
                </div>
                </html_content>
                <css_content>
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
                </css_content>
                <js_content>
                function submitAnswer(answer) {
                  submitInteraction({
                    answer: answer,
                    question: "What is 2 + 2?",
                    correct: answer === "4",
                    timeSpent: Date.now() - startTime
                  });
                }
                var startTime = Date.now();
                </js_content>
                </interactive_js_block>
             """),
        ] 