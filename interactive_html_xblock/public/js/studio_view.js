function StudioView(runtime, element) {
    'use strict';
    
    var handlerUrl = runtime.handlerUrl(element, 'studio_submit');
    
    // Setup form handling
    $(element).find('.save-button').bind('click', function () {
        var formData = {
            display_name: $(element).find('input[name=xb_display_name]').val(),
            html_content: $(element).find('textarea[name=xb_html_content]').val(),
            css_content: $(element).find('textarea[name=xb_css_content]').val(),
            js_content: $(element).find('textarea[name=xb_js_content]').val(),
            weight: parseInt($(element).find('input[name=xb_weight]').val()) || 1,
            enable_debug_mode: $(element).find('input[name=xb_enable_debug_mode]').is(':checked'),
            auto_grade_enabled: $(element).find('input[name=xb_auto_grade_enabled]').is(':checked'),
            correct_answers: $(element).find('textarea[name=xb_correct_answers]').val(),
            show_feedback_to_learners: $(element).find('input[name=xb_show_feedback_to_learners]').is(':checked'),
            show_previous_response: $(element).find('input[name=xb_show_previous_response]').is(':checked'),
            enable_instructor_view: $(element).find('input[name=xb_enable_instructor_view]').is(':checked'),
            allowed_external_urls: []
        };
        
        // Validate required fields
        if (!formData.html_content.trim()) {
            alert('HTML content cannot be empty');
            return;
        }
        
        // Validate correct_answers JSON if auto-grading is enabled
        if (formData.auto_grade_enabled && formData.correct_answers.trim()) {
            try {
                JSON.parse(formData.correct_answers);
            } catch (e) {
                alert('Correct Answers must be valid JSON format');
                return;
            }
        }
        
        // Show loading state
        var saveButton = $(element).find('.save-button');
        var originalText = saveButton.text();
        saveButton.text('Saving...').prop('disabled', true);
        
        if ('notify' in runtime) {
            runtime.notify('save', { state: 'start' });
        }
        
        // Send data to XBlock
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(formData),
            contentType: "application/json",
            success: function(response) {
                console.log('InteractiveJSBlock: Save successful', response);
                saveButton.text(originalText).prop('disabled', false);
                if ('notify' in runtime) {
                    runtime.notify('save', { state: 'end' });
                }
            },
            error: function(xhr, status, error) {
                console.error('InteractiveJSBlock: Save failed', error);
                saveButton.text(originalText).prop('disabled', false);
                alert('Failed to save block: ' + error);
            }
        });
    });
    
    $(element).find('.cancel-button').bind('click', function () {
        if ('notify' in runtime) {
            runtime.notify('cancel', {});
        }
    });
} 