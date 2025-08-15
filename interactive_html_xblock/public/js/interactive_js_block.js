/* InteractiveJSBlock Student View JavaScript */

function InteractiveJSBlockView(runtime, element) {
    'use strict';
    
    // Global variables for the block
    var blockId = element.getAttribute('data-block-id');
    var displayName = element.querySelector('.interactive-js-block').getAttribute('aria-label');
    var isDebugMode = element.querySelector('.debug-panel') !== null;
    var isStaff = element.querySelector('.staff-panel') !== null;
    
    // Create the XBlockInterface for safe JS → XBlock communication
    var XBlockInterface = {
        postMessage: function({ type, payload }) {
            if (type === 'interaction') {
                this.saveInteraction(payload);
            } else if (type === 'error') {
                this.showError(payload);
            }
        },
        
        saveInteraction: function(data) {
            var self = this;
            
            // Check if runtime is available
            if (typeof runtime === 'undefined') {
                console.error('InteractiveJSBlock: runtime not available');
                this.showError('Runtime not available - cannot save interaction');
                return;
            }
            
            var handlerUrl = runtime.handlerUrl(element, 'save_interaction');
            
            // Show loading indicator
            this.showLoading(true);
            
            $.ajax({
                type: "POST",
                url: handlerUrl,
                data: JSON.stringify(data),
                contentType: "application/json",
                success: function(response) {
                    self.showLoading(false);
                    if (response.status === 'ok') {
                        console.log('Interaction saved:', response.message);
                        self.updateDebugInfo(response);
                        self.showSuccess('Interaction saved successfully');
                        
                        // Show feedback if available
                        if (response.show_feedback) {
                            self.showFeedback(response);
                        }
                        
                        // Update staff panel if staff
                        if (isStaff) {
                            self.updateStaffPanel(response);
                        }
                    } else {
                        console.error('Failed to save interaction:', response.message);
                        self.showError('Failed to save interaction: ' + response.message);
                    }
                },
                error: function(xhr, status, error) {
                    self.showLoading(false);
                    console.error('AJAX error:', error);
                    self.showError('Network error: ' + error);
                }
            });
        },
        
        showFeedback: function(response) {
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
                
                // Update score - use weight from response if available, otherwise use a default
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
        },
        
        updateStaffPanel: function(response) {
            // Update staff panel with new data
            var staffResponse = element.querySelector('#staff-learner-response');
            var staffInteractionCount = element.querySelector('#staff-interaction-count');
            var staffLastInteraction = element.querySelector('#staff-last-interaction');
            var staffIsCorrect = element.querySelector('#staff-is-correct');
            var staffScore = element.querySelector('#staff-score');
            var staffFeedbackMessage = element.querySelector('#staff-feedback-message');
            
            if (staffResponse && response.learner_response) {
                staffResponse.textContent = JSON.stringify(response.learner_response, null, 2);
            }
            
            if (staffInteractionCount && response.interaction_count !== undefined) {
                staffInteractionCount.textContent = response.interaction_count;
            }
            
            if (staffLastInteraction && response.last_interaction_time) {
                staffLastInteraction.textContent = response.last_interaction_time;
            }
            
            if (staffIsCorrect && response.is_correct !== undefined) {
                staffIsCorrect.textContent = response.is_correct ? 'Yes' : 'No';
            }
            
            if (staffScore && response.score !== undefined) {
                var weight = response.weight || 1;
                staffScore.textContent = response.score + '/' + weight;
            }
            
            if (staffFeedbackMessage && response.feedback_message) {
                staffFeedbackMessage.textContent = response.feedback_message;
            }
        },
        
        showError: function(message) {
            console.error('InteractiveJSBlock Error:', message);
            var errorDisplay = element.querySelector('#error-display');
            var errorMessage = errorDisplay ? errorDisplay.querySelector('.error-message') : null;
            if (errorDisplay && errorMessage) {
                errorMessage.textContent = message;
                errorDisplay.style.display = 'block';
                
                // Hide error after 5 seconds
                setTimeout(function() {
                    errorDisplay.style.display = 'none';
                }, 5000);
            }
        },
        
        showLoading: function(show) {
            var loadingIndicator = element.querySelector('#loading-indicator');
            if (loadingIndicator) {
                loadingIndicator.style.display = show ? 'block' : 'none';
            }
            
            var block = element.querySelector('.interactive-js-block');
            if (block) {
                if (show) {
                    block.classList.add('loading');
                } else {
                    block.classList.remove('loading');
                }
            }
        },
        
        showSuccess: function(message) {
            console.log('InteractiveJSBlock Success:', message);
            // You can add a success indicator here if needed
        },
        
        updateDebugInfo: function(response) {
            var countElement = element.querySelector('#interaction-count-debug');
            var lastElement = element.querySelector('#last-interaction-debug');
            var isCorrectElement = element.querySelector('#is-correct-debug');
            var scoreElement = element.querySelector('#score-debug');
            
            if (countElement && response.interaction_count !== undefined) {
                countElement.textContent = response.interaction_count;
            }
            if (lastElement && response.last_interaction_time) {
                lastElement.textContent = response.last_interaction_time;
            }
            if (isCorrectElement && response.is_correct !== undefined) {
                isCorrectElement.textContent = response.is_correct ? 'Yes' : 'No';
            }
            if (scoreElement && response.score !== undefined) {
                var weight = response.weight || 1;
                scoreElement.textContent = response.score + '/' + weight;
            }
        }
    };
    
    // Make submitInteraction globally available for author's JavaScript
    window.submitInteraction = function(data) {
        if (typeof data !== 'object') {
            console.error('submitInteraction: data must be an object');
            return;
        }
        
        // Add timestamp if not provided
        if (!data.timestamp) {
            data.timestamp = new Date().toISOString();
        }
        
        // Add block context
        data.block_id = blockId;
        data.display_name = displayName;
        
        console.log('submitInteraction called with:', data);
        XBlockInterface.saveInteraction(data);
    };
    
    // Function to apply author's CSS
    function applyAuthorCSS() {
        var cssContent = element.querySelector('style[data-author-css]');
        if (cssContent) {
            try {
                var styleElement = document.createElement('style');
                styleElement.setAttribute('data-interactive-js-block', blockId);
                styleElement.textContent = cssContent.textContent;
                document.head.appendChild(styleElement);
                console.log('Author CSS applied for block:', blockId);
            } catch (error) {
                console.error('Error applying author CSS:', error);
                XBlockInterface.showError('CSS error: ' + error.message);
            }
        }
    }
    
    // Function to execute author's JavaScript
    function executeAuthorJS() {
        var jsContent = element.querySelector('script[data-author-js]');
        if (jsContent) {
            try {
                // Create a script element to execute the author's JavaScript
                var scriptElement = document.createElement('script');
                scriptElement.setAttribute('data-interactive-js-block', blockId);
                scriptElement.textContent = jsContent.textContent;
                document.head.appendChild(scriptElement);
                console.log('Author JavaScript executed for block:', blockId);
            } catch (error) {
                console.error('Error executing author JavaScript:', error);
                XBlockInterface.showError('JavaScript error: ' + error.message);
            }
        }
    }
    
    // Initialize the student view
    function initializeStudentView() {
        console.log('InteractiveJSBlock: Initializing student view for block:', blockId);
        
        // Setup error handling
        setupErrorHandling();
        
        // Setup accessibility features
        setupAccessibility();
        
        // Setup keyboard navigation
        setupKeyboardNavigation();
        
        // Apply author's CSS first
        applyAuthorCSS();
        
        // Execute author's JavaScript after a short delay to ensure everything is ready
        setTimeout(function() {
            executeAuthorJS();
        }, 100);
        
        // Log initialization
        console.log('InteractiveJSBlock: Student view ready for block:', blockId);
    }
    
    // Setup error handling
    function setupErrorHandling() {
        // Global error handler for this block
        element.addEventListener('error', function(event) {
            console.error('InteractiveJSBlock: Global error:', event.error);
            XBlockInterface.showError('JavaScript error: ' + event.error.message);
        });
        
        // Unhandled promise rejection handler for this block
        element.addEventListener('unhandledrejection', function(event) {
            console.error('InteractiveJSBlock: Unhandled promise rejection:', event.reason);
            XBlockInterface.showError('Promise error: ' + event.reason);
        });
    }
    
    // Setup accessibility features
    function setupAccessibility() {
        // Add ARIA labels and roles
        var block = element.querySelector('.interactive-js-block');
        if (block) {
            block.setAttribute('role', 'region');
            block.setAttribute('aria-label', 'Interactive content block');
        }
        
        // Add focus management
        var focusableElements = element.querySelectorAll('button, input, textarea, select, [tabindex]:not([tabindex="-1"])');
        focusableElements.forEach(function(el) {
            el.addEventListener('focus', function() {
                this.classList.add('focused');
            });
            
            el.addEventListener('blur', function() {
                this.classList.remove('focused');
            });
        });
    }
    
    // Setup keyboard navigation
    function setupKeyboardNavigation() {
        // Handle keyboard shortcuts
        element.addEventListener('keydown', function(event) {
            // Ctrl+Enter to submit interaction (if available)
            if (event.ctrlKey && event.key === 'Enter') {
                var submitButton = element.querySelector('[data-action="submit"]');
                if (submitButton) {
                    submitButton.click();
                }
            }
        });
    }
    
    // Initialize when DOM is ready
    $(document).ready(function() {
        initializeStudentView();
    });
    
    // Public API
    return {
        showError: XBlockInterface.showError,
        showSuccess: XBlockInterface.showSuccess,
        showLoading: XBlockInterface.showLoading,
        updateDebugInfo: XBlockInterface.updateDebugInfo,
        showFeedback: XBlockInterface.showFeedback
    };
}

// Initialize when DOM is ready
$(function() {
    // The actual initialization is handled by the XBlock framework
    // This is just a fallback
    console.log('InteractiveJSBlock: Student view script loaded');
}); 