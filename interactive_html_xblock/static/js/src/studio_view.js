/* InteractiveJSBlock Studio View JavaScript */

function StudioView(runtime, element) {
    'use strict';
    
    // Initialize the studio view
    function initializeStudio() {
        console.log('InteractiveJSBlock: Initializing studio view');
        
        // Setup tab navigation
        setupTabNavigation();
        
        // Setup form handling
        setupFormHandling();
        
        // Setup preview functionality
        setupPreview();
        
        // Setup test interaction functionality
        setupTestInteraction();
        
        // Setup reset functionality
        setupReset();
        
        // Setup accessibility
        setupAccessibility();
        
        console.log('InteractiveJSBlock: Studio view ready');
    }
    
    // Setup tab navigation
    function setupTabNavigation() {
        var tabButtons = element.querySelectorAll('.tab-button');
        var tabPanes = element.querySelectorAll('.tab-pane');
        
        tabButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                var targetTab = this.getAttribute('data-tab');
                
                // Update ARIA attributes
                tabButtons.forEach(function(btn) {
                    btn.setAttribute('aria-selected', 'false');
                });
                this.setAttribute('aria-selected', 'true');
                
                // Remove active class from all buttons and panes
                tabButtons.forEach(function(btn) {
                    btn.classList.remove('active');
                });
                tabPanes.forEach(function(pane) {
                    pane.classList.remove('active');
                    pane.style.display = 'none';
                });
                
                // Add active class to clicked button and corresponding pane
                this.classList.add('active');
                var targetPane = element.querySelector('#' + targetTab + '-tab');
                if (targetPane) {
                    targetPane.classList.add('active');
                    targetPane.style.display = 'block';
                }
            });
        });
    }
    
    // Setup form handling
    function setupFormHandling() {
        var saveButton = element.querySelector('#save-button');
        if (saveButton) {
            saveButton.addEventListener('click', function() {
                saveBlock();
            });
        }
    }
    
    // Save block data
    function saveBlock() {
        // Get form data
        var formData = {
            display_name: getFieldValue('display_name'),
            html_content: getFieldValue('html_content'),
            css_content: getFieldValue('css_content'),
            js_content: getFieldValue('js_content'),
            weight: parseInt(getFieldValue('weight')) || 1,
            enable_debug_mode: getCheckboxValue('enable_debug_mode'),
            auto_grade_enabled: getCheckboxValue('auto_grade_enabled'),
            allowed_external_urls: parseJsonField('allowed_external_urls')
        };
        
        // Validate required fields
        if (!formData.html_content.trim()) {
            showError('HTML content cannot be empty');
            return;
        }
        
        // Show loading state
        var saveButton = element.querySelector('#save-button');
        var originalText = saveButton.querySelector('.btn-text').textContent;
        saveButton.classList.add('saving');
        saveButton.disabled = true;
        
        // Send data to XBlock
        var handlerUrl = runtime.handlerUrl(element, 'save_interaction');
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(formData),
            contentType: "application/json",
            success: function(response) {
                console.log('InteractiveJSBlock: Save successful', response);
                saveButton.classList.remove('saving');
                saveButton.disabled = false;
                showSuccess('Block saved successfully!');
            },
            error: function(xhr, status, error) {
                console.error('InteractiveJSBlock: Save failed', error);
                saveButton.classList.remove('saving');
                saveButton.disabled = false;
                showError('Failed to save block: ' + error);
            }
        });
    }
    
    // Setup preview functionality
    function setupPreview() {
        var previewButton = element.querySelector('#preview-button');
        var modal = element.querySelector('#preview-modal');
        var closeButton = modal.querySelector('.close');
        var previewContent = modal.querySelector('#preview-content');
        
        if (previewButton) {
            previewButton.addEventListener('click', function() {
                showPreview();
            });
        }
        
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                hidePreview();
            });
        }
        
        // Close modal when clicking outside
        window.addEventListener('click', function(event) {
            if (event.target === modal) {
                hidePreview();
            }
        });
        
        // Close modal with Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && modal.style.display === 'block') {
                hidePreview();
            }
        });
    }
    
    // Show preview
    function showPreview() {
        var modal = element.querySelector('#preview-modal');
        var previewContent = modal.querySelector('#preview-content');
        
        // Get current form values
        var htmlContent = getFieldValue('html_content');
        var cssContent = getFieldValue('css_content');
        var jsContent = getFieldValue('js_content');
        
        // Create preview HTML
        var previewHtml = `
            <div class="preview-container">
                <style>${cssContent}</style>
                <div class="preview-html">${htmlContent}</div>
                <script>
                    // Mock submitInteraction function for preview
                    window.submitInteraction = function(data) {
                        console.log('Preview: submitInteraction called with:', data);
                        alert('Preview: Interaction data would be sent: ' + JSON.stringify(data));
                    };
                    ${jsContent}
                </script>
            </div>
        `;
        
        previewContent.innerHTML = previewHtml;
        modal.style.display = 'block';
        modal.setAttribute('aria-hidden', 'false');
    }
    
    // Hide preview
    function hidePreview() {
        var modal = element.querySelector('#preview-modal');
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
    }
    
    // Setup test interaction functionality
    function setupTestInteraction() {
        var testButton = element.querySelector('#test-interaction-button');
        if (testButton) {
            testButton.addEventListener('click', function() {
                testInteraction();
            });
        }
    }
    
    // Test interaction
    function testInteraction() {
        console.log('InteractiveJSBlock: Testing interaction');
        
        // Create test data
        var testData = {
            test: true,
            timestamp: new Date().toISOString(),
            message: 'Test interaction from studio'
        };
        
        // Show test result
        showSuccess('Test interaction data: ' + JSON.stringify(testData, null, 2));
    }
    
    // Setup reset functionality
    function setupReset() {
        var resetButton = element.querySelector('#reset-button');
        if (resetButton) {
            resetButton.addEventListener('click', function() {
                showConfirmDialog('Are you sure you want to reset all fields to their default values?', function() {
                    resetFields();
                });
            });
        }
    }
    
    // Reset all fields to defaults
    function resetFields() {
        // Reset to default values
        setFieldValue('display_name', 'Interactive JS Block');
        setFieldValue('html_content', '<div class="interactive-content">\n  <h3>Interactive Content</h3>\n  <p>Add your interactive HTML here.</p>\n</div>');
        setFieldValue('css_content', '.interactive-content {\n  padding: 20px;\n  border: 1px solid #ccc;\n  border-radius: 5px;\n}');
        setFieldValue('js_content', '// Example: submitInteraction({ answer: "user input", timeSpent: 30 });\nconsole.log("Interactive JS loaded");');
        setFieldValue('weight', '1');
        setCheckboxValue('enable_debug_mode', false);
        setCheckboxValue('auto_grade_enabled', false);
        setFieldValue('allowed_external_urls', '[]');
        
        showSuccess('Fields reset to default values');
    }
    
    // Setup accessibility
    function setupAccessibility() {
        // Add keyboard navigation for tabs
        var tabButtons = element.querySelectorAll('.tab-button');
        tabButtons.forEach(function(button, index) {
            button.addEventListener('keydown', function(event) {
                if (event.key === 'ArrowRight') {
                    var nextIndex = (index + 1) % tabButtons.length;
                    tabButtons[nextIndex].click();
                    tabButtons[nextIndex].focus();
                } else if (event.key === 'ArrowLeft') {
                    var prevIndex = (index - 1 + tabButtons.length) % tabButtons.length;
                    tabButtons[prevIndex].click();
                    tabButtons[prevIndex].focus();
                }
            });
        });
    }
    
    // Show confirmation dialog
    function showConfirmDialog(message, onConfirm) {
        var modal = element.querySelector('#confirm-modal');
        var messageElement = modal.querySelector('#confirm-message');
        var okButton = modal.querySelector('#confirm-ok');
        var cancelButton = modal.querySelector('#confirm-cancel');
        
        messageElement.textContent = message;
        modal.style.display = 'block';
        modal.setAttribute('aria-hidden', 'false');
        
        // Focus the OK button
        okButton.focus();
        
        // Handle OK button
        var handleOk = function() {
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
            okButton.removeEventListener('click', handleOk);
            cancelButton.removeEventListener('click', handleCancel);
            onConfirm();
        };
        
        // Handle Cancel button
        var handleCancel = function() {
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
            okButton.removeEventListener('click', handleOk);
            cancelButton.removeEventListener('click', handleCancel);
        };
        
        okButton.addEventListener('click', handleOk);
        cancelButton.addEventListener('click', handleCancel);
    }
    
    // Show success message
    function showSuccess(message) {
        var successElement = element.querySelector('#success-message');
        if (successElement) {
            successElement.textContent = message;
            successElement.style.display = 'block';
            setTimeout(function() {
                successElement.style.display = 'none';
            }, 3000);
        }
        console.log('Success:', message);
    }
    
    // Show error message
    function showError(message) {
        var errorElement = element.querySelector('#error-message');
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
            setTimeout(function() {
                errorElement.style.display = 'none';
            }, 5000);
        }
        console.error('Error:', message);
    }
    
    // Helper functions
    function getFieldValue(fieldName) {
        var field = element.querySelector('[name="' + fieldName + '"]');
        return field ? field.value : '';
    }
    
    function setFieldValue(fieldName, value) {
        var field = element.querySelector('[name="' + fieldName + '"]');
        if (field) {
            field.value = value;
        }
    }
    
    function getCheckboxValue(fieldName) {
        var field = element.querySelector('[name="' + fieldName + '"]');
        return field ? field.checked : false;
    }
    
    function setCheckboxValue(fieldName, value) {
        var field = element.querySelector('[name="' + fieldName + '"]');
        if (field) {
            field.checked = value;
        }
    }
    
    function parseJsonField(fieldName) {
        var value = getFieldValue(fieldName);
        try {
            return JSON.parse(value);
        } catch (e) {
            return [];
        }
    }
    
    // Initialize when DOM is ready
    $(function() {
        initializeStudio();
    });
    
    // Return public methods
    return {
        saveBlock: saveBlock,
        showPreview: showPreview,
        hidePreview: hidePreview,
        testInteraction: testInteraction,
        resetFields: resetFields,
        showSuccess: showSuccess,
        showError: showError
    };
} 