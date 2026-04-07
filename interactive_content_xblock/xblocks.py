"""
This is the core logic for the InteractiveContentXBlock
"""
from xblock.core import XBlock
try:
    from xblock.completable import CompletableXBlockMixin
except ImportError:
    # Fallback for older XBlock versions
    class CompletableXBlockMixin:
        pass

from .models import InteractiveContentXBlockModelMixin
from .views import InteractiveContentXBlockViewMixin


@XBlock.wants('user')
@XBlock.wants('i18n')
class InteractiveContentXBlock(
        InteractiveContentXBlockModelMixin,
        InteractiveContentXBlockViewMixin,
        CompletableXBlockMixin,
        XBlock,
):
    """
    XBlock for creating interactive HTML/CSS/JS content with learner interaction tracking.

    This XBlock allows authors to define custom HTML, CSS, and JavaScript content
    and automatically captures learner interactions in JSON format for analytics,
    grading, or state restoration.
    """

    @staticmethod
    def workbench_scenarios():
        """Create canned scenarios for display in the workbench."""
        return [
            ("InteractiveContentXBlock",
             """<interactive_content_xblock/>
             """),
            ("Multiple InteractiveContentXBlock",
             """<vertical_demo>
                <interactive_content_xblock/>
                <interactive_content_xblock/>
                <interactive_content_xblock/>
                </vertical_demo>
             """),
            ("InteractiveContentXBlock with Quiz",
             """<interactive_content_xblock>
                <html_content>
                <div class="quiz">
                  <h3>Geography Quiz</h3>
                  <p>What is the capital of France?</p>
                  <div class="options">
                    <button onclick="submitAnswer('Paris')">Paris</button>
                    <button onclick="submitAnswer('London')">London</button>
                    <button onclick="submitAnswer('Berlin')">Berlin</button>
                  </div>
                  <div id="result"></div>
                </div>
                </html_content>
                <css_content>
                .quiz {
                  padding: 20px;
                  border: 2px solid #007bff;
                  border-radius: 8px;
                  background: #f8f9fa;
                }
                .options {
                  display: flex;
                  gap: 10px;
                  margin-top: 12px;
                }
                .options button {
                  padding: 10px 20px;
                  border: 1px solid #007bff;
                  border-radius: 4px;
                  background: white;
                  cursor: pointer;
                  font-size: 14px;
                }
                .options button:hover {
                  background: #007bff;
                  color: white;
                }
                </css_content>
                <js_content>
                var startTime = Date.now();

                function submitAnswer(answer) {
                  submitInteraction({
                    answer: answer,
                    correct: answer === "Paris",
                    timeSpent: Math.round((Date.now() - startTime) / 1000)
                  });
                }
                </js_content>
                </interactive_content_xblock>
             """),
        ] 