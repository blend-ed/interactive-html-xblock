/* InteractiveJSBlock JavaScript */

function InteractiveJSBlockView(runtime, element) {
    'use strict';
    

    var blockId = element.getAttribute('data-block-id');
    
    // Initialize the view
    function initializeView() {
        console.log('InteractiveJSBlock: Initializing view');
        

        
        // Initialize author's CSS and JS
        initializeAuthorContent();
        
        // Set up global submitInteraction function
        window.submitInteraction = submitInteraction;
        
        console.log('InteractiveJSBlock: View initialized');
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
                var script = document.createElement('script');
                script.textContent = jsElement.textContent;
                element.appendChild(script);
            } catch (e) {
                console.error('InteractiveJSBlock: Error executing author JavaScript:', e);
            }
        }
    }
    
    // Global submitInteraction function
    function submitInteraction(data) {
        console.log('InteractiveJSBlock: submitInteraction called with:', data);
        
        if (!runtime || !runtime.handlerUrl) {
            console.error('InteractiveJSBlock: Runtime not available - cannot save interaction');
            return;
        }
        
        var handlerUrl = runtime.handlerUrl(element, 'save_interaction');
        
        $.ajax({
            type: 'POST',
            url: handlerUrl,
            data: JSON.stringify(data),
            success: function(response) {
                console.log('InteractiveJSBlock Success:', response.message);
                
                if (response.status === 'ok') {
                    // Update debug info
                    updateDebugInfo(response);
                    
                    // Show feedback if enabled
                    if (response.show_feedback) {
                        showFeedback(response);
                    }
                    

                    
                    // Publish grade if auto-grading is enabled
                    if (response.publish_grade) {
                        publishGrade(response.score, response.weight);
                    }
                } else {
                    console.error('InteractiveJSBlock Error:', response.message);
                }
            },
            error: function(xhr, status, error) {
                console.error('InteractiveJSBlock: Error saving interaction:', error);
                showError('Failed to save interaction: ' + error);
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
                statusIcon.textContent = '✓';
                statusText.textContent = 'Correct';
                feedbackStatus.className = 'feedback-status correct';
            } else {
                statusIcon.textContent = '✗';
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
    

    
    // Publish grade
    function publishGrade(score, weight) {
        if (runtime && runtime.publish) {
            var grade = {
                value: score,
                max_value: weight,
                user_id: runtime.user_id
            };
            runtime.publish(element, 'grade', grade);
        }
    }
    
    // Show error message
    function showError(message) {
        console.error('InteractiveJSBlock Error:', message);
        // You can implement a more sophisticated error display here
    }
    
    // Show message
    function showMessage(message, type) {
        var notification = document.createElement('div');
        var backgroundColor = '#28a745'; // success
        if (type === 'error') {
            backgroundColor = '#dc3545';
        } else if (type === 'info') {
            backgroundColor = '#17a2b8';
        }
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${backgroundColor};
            color: white;
            padding: 12px 20px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            z-index: 10000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            max-width: 400px;
            word-wrap: break-word;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(function() {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 8000); // Show info messages longer
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