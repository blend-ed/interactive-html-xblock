/* InteractiveContentXBlock JavaScript */

function InteractiveContentXBlockView(runtime, element) {
    'use strict';

    // Initialize the view
    function initializeView() {
        // Set up global submitInteraction BEFORE author JS runs
        window.submitInteraction = submitInteraction;

        // Initialize author's CSS and JS
        initializeAuthorContent();
    }

    // Initialize author's CSS and JavaScript content
    function initializeAuthorContent() {
        var cssElement = element.querySelector('#author-css');
        var jsElement = element.querySelector('#author-js');

        if (cssElement && cssElement.textContent.trim()) {
            var style = document.createElement('style');
            style.textContent = cssElement.textContent;
            element.appendChild(style);
        }

        if (jsElement && jsElement.textContent.trim()) {
            try {
                // Append as a <script> to document.head so function
                // declarations land in true global scope — accessible
                // to onclick handlers in both LMS and Studio iframe.
                var script = document.createElement('script');
                script.textContent = jsElement.textContent;
                document.head.appendChild(script);
            } catch (e) {
                console.error('InteractiveContentXBlock: Error executing author JavaScript:', e);
            }
        }
    }

    // Global submitInteraction function
    function submitInteraction(data) {
        if (!runtime || !runtime.handlerUrl) {
            console.error('InteractiveContentXBlock: Runtime not available - cannot save interaction');
            return;
        }

        var handlerUrl = runtime.handlerUrl(element, 'save_interaction');

        $.ajax({
            type: 'POST',
            url: handlerUrl,
            data: JSON.stringify(data),
            success: function(response) {
                if (response.status === 'ok') {
                    // Update debug info
                    updateDebugInfo(response);

                    // Show feedback if enabled
                    if (response.show_feedback) {
                        showFeedback(response);
                    }
                } else {
                    console.error('InteractiveContentXBlock Error:', response.message);
                }
            },
            error: function(xhr, status, error) {
                console.error('InteractiveContentXBlock: Error saving interaction:', error);
            }
        });
    }

    // Update debug information
    function updateDebugInfo(response) {
        var interactionCount = element.querySelector('#debug-interaction-count');
        var lastInteraction = element.querySelector('#debug-last-interaction');
        var isCorrect = element.querySelector('#debug-is-correct');
        var score = element.querySelector('#debug-score');

        if (interactionCount) interactionCount.textContent = response.interaction_count || 0;
        if (lastInteraction) lastInteraction.textContent = response.last_interaction_time || '';
        if (isCorrect) isCorrect.textContent = response.is_correct ? 'Yes' : 'No';
        if (score) {
            var weight = response.weight || 1;
            score.textContent = (response.score || 0) + '/' + weight;
        }
    }

    // Show feedback to learner
    function showFeedback(response) {
        var feedbackDisplay = element.querySelector('#feedback-display');
        var statusIcon = element.querySelector('#status-icon');
        var statusText = element.querySelector('#status-text');
        var scoreValue = element.querySelector('#score-value');
        var feedbackMessageText = element.querySelector('#feedback-message-text');
        var feedbackStatus = element.querySelector('#feedback-status');

        if (feedbackDisplay && response.is_correct !== undefined) {
            // Update status
            if (response.is_correct) {
                statusIcon.textContent = '\u2713';
                statusText.textContent = 'Correct';
                feedbackStatus.className = 'feedback-status correct';
            } else {
                statusIcon.textContent = '\u2717';
                statusText.textContent = 'Incorrect';
                feedbackStatus.className = 'feedback-status incorrect';
            }

            // Update score
            if (scoreValue && response.score !== undefined) {
                var weight = response.weight || 1;
                scoreValue.textContent = response.score + '/' + weight;
            }

            // Update feedback message
            if (feedbackMessageText && response.feedback_message) {
                feedbackMessageText.textContent = response.feedback_message;
            }

            // Show the feedback display
            feedbackDisplay.style.display = 'block';

            // Hide after 5 seconds
            setTimeout(function() {
                feedbackDisplay.style.display = 'none';
            }, 5000);
        }
    }

    // Initialize when DOM is ready
    $(document).ready(function() {
        initializeView();
    });

    // Public API
    return {
        submitInteraction: submitInteraction
    };
}
