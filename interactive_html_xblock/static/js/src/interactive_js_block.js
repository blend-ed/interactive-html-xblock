/* InteractiveJSBlock Student View JavaScript */

function InteractiveJSBlockView(runtime, element) {
    'use strict';
    
    // Initialize the student view
    function initializeStudentView() {
        console.log('InteractiveJSBlock: Initializing student view');
        
        // Setup error handling
        setupErrorHandling();
        
        // Setup accessibility features
        setupAccessibility();
        
        // Setup keyboard navigation
        setupKeyboardNavigation();
        
        // Log initialization
        console.log('InteractiveJSBlock: Student view ready');
    }
    
    // Setup error handling
    function setupErrorHandling() {
        // Global error handler
        window.addEventListener('error', function(event) {
            console.error('InteractiveJSBlock: Global error:', event.error);
            showError('JavaScript error: ' + event.error.message);
        });
        
        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', function(event) {
            console.error('InteractiveJSBlock: Unhandled promise rejection:', event.reason);
            showError('Promise error: ' + event.reason);
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
        document.addEventListener('keydown', function(event) {
            // Ctrl+Enter to submit interaction (if available)
            if (event.ctrlKey && event.key === 'Enter') {
                var submitButton = element.querySelector('[data-action="submit"]');
                if (submitButton) {
                    submitButton.click();
                }
            }
        });
    }
    
    // Show error message
    function showError(message) {
        var errorDisplay = element.querySelector('#error-display');
        var errorMessage = errorDisplay ? errorDisplay.querySelector('.error-message') : null;
        
        if (errorDisplay && errorMessage) {
            errorMessage.textContent = message;
            errorDisplay.style.display = 'block';
            
            // Announce to screen readers
            errorDisplay.setAttribute('aria-live', 'polite');
            
            // Hide after 5 seconds
            setTimeout(function() {
                errorDisplay.style.display = 'none';
            }, 5000);
        }
        
        console.error('InteractiveJSBlock Error:', message);
    }
    
    // Show success message
    function showSuccess(message) {
        console.log('InteractiveJSBlock Success:', message);
        
        // You can implement a success notification here
        // For now, we'll just log it
    }
    
    // Update debug information
    function updateDebugInfo(response) {
        var countElement = element.querySelector('#interaction-count');
        var countDebugElement = element.querySelector('#interaction-count-debug');
        var lastElement = element.querySelector('#last-interaction');
        var lastDebugElement = element.querySelector('#last-interaction-debug');
        
        if (countElement) {
            countElement.textContent = response.interaction_count;
        }
        if (countDebugElement) {
            countDebugElement.textContent = response.interaction_count;
        }
        if (lastElement) {
            lastElement.textContent = new Date().toISOString();
        }
        if (lastDebugElement) {
            lastDebugElement.textContent = new Date().toISOString();
        }
    }
    
    // Show loading state
    function showLoading(show) {
        var indicator = element.querySelector('#loading-indicator');
        if (indicator) {
            indicator.style.display = show ? 'block' : 'none';
        }
        
        var block = element.querySelector('.interactive-js-block');
        if (block) {
            if (show) {
                block.classList.add('loading');
            } else {
                block.classList.remove('loading');
            }
        }
    }
    
    // Public API
    return {
        showError: showError,
        showSuccess: showSuccess,
        showLoading: showLoading,
        updateDebugInfo: updateDebugInfo
    };
}

// Initialize when DOM is ready
$(function() {
    // The actual initialization is handled by the XBlock framework
    // This is just a fallback
    console.log('InteractiveJSBlock: Student view script loaded');
}); 