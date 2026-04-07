function StudioView(runtime, element) {
    'use strict';

    var handlerUrl = runtime.handlerUrl(element, 'studio_submit');

    // ── Grading form: multi-field row management ──

    function addFieldRow(name, value) {
        var row = $(
            '<div class="grading-field-row" style="display:flex;gap:8px;margin-bottom:6px;align-items:center;">' +
              '<input class="input setting-input grading-field-name" type="text" placeholder="Field name" style="flex:1;" />' +
              '<input class="input setting-input grading-field-value" type="text" placeholder="Expected value" style="flex:1;" />' +
              '<a href="#" class="grading-remove-field" title="Remove" style="color:#c00;text-decoration:none;font-weight:bold;padding:0 6px;font-size:1.2em;">&times;</a>' +
            '</div>'
        );
        row.find('.grading-field-name').val(name || '');
        row.find('.grading-field-value').val(value || '');
        $(element).find('#grading-fields-list').append(row);
    }

    $(element).find('#grading-add-field').on('click', function(e) {
        e.preventDefault();
        addFieldRow('', '');
        updateTestInputs();
    });

    $(element).find('#grading-fields-list').on('click', '.grading-remove-field', function(e) {
        e.preventDefault();
        $(this).closest('.grading-field-row').remove();
        updateTestInputs();
    });

    // ── Grading form: show/hide panels ──

    function updateGradingPanels() {
        var mode = $(element).find('#xb_grading_mode').val();
        var autoGrade = $(element).find('#xb_auto_grade_enabled').val() === '1';
        $(element).find('#grading-single-panel').toggle(autoGrade && mode === 'single');
        $(element).find('#grading-multi-panel').toggle(autoGrade && mode === 'multi');
    }

    function updateGradingSectionVisibility() {
        var autoGrade = $(element).find('#xb_auto_grade_enabled').val() === '1';
        $(element).find('#grading-mode-wrapper').toggle(autoGrade);
        updateGradingPanels();
        updateTestInputs();
    }

    $(element).find('#xb_grading_mode').on('change', function() {
        updateGradingPanels();
        updateTestInputs();
    });
    $(element).find('#xb_auto_grade_enabled').on('change', updateGradingSectionVisibility);

    // ── Grading form: init from existing JSON ──

    (function initGradingForm() {
        var raw = $(element).find('#xb_correct_answers').val().trim();
        var data = {};
        if (raw) {
            try { data = JSON.parse(raw); } catch (e) { /* leave empty */ }
        }

        $(element).find('#xb_correct_feedback').val(data.correct_feedback || '');
        $(element).find('#xb_incorrect_feedback').val(data.incorrect_feedback || '');

        if (data.fields && typeof data.fields === 'object' && Object.keys(data.fields).length > 0) {
            $(element).find('#xb_grading_mode').val('multi');
            $.each(data.fields, function(name, value) {
                addFieldRow(name, value);
            });
        } else if (data.answer !== undefined && data.answer !== '') {
            $(element).find('#xb_grading_mode').val('single');
            $(element).find('#xb_single_answer').val(data.answer);
        } else {
            $(element).find('#xb_grading_mode').val('none');
        }

        updateGradingSectionVisibility();
    })();

    // ── Grading form: build JSON from form fields ──

    function buildCorrectAnswersJSON() {
        var result = {};
        var mode = $(element).find('#xb_grading_mode').val();
        var autoGrade = $(element).find('#xb_auto_grade_enabled').val() === '1';

        var cf = $(element).find('#xb_correct_feedback').val().trim();
        var icf = $(element).find('#xb_incorrect_feedback').val().trim();
        if (cf) result.correct_feedback = cf;
        if (icf) result.incorrect_feedback = icf;

        if (autoGrade && mode === 'single') {
            var answer = $(element).find('#xb_single_answer').val().trim();
            if (answer) result.answer = answer;
        } else if (autoGrade && mode === 'multi') {
            var fields = {};
            $(element).find('.grading-field-row').each(function() {
                var name = $(this).find('.grading-field-name').val().trim();
                var value = $(this).find('.grading-field-value').val().trim();
                if (name) fields[name] = value;
            });
            if (Object.keys(fields).length > 0) result.fields = fields;
        }

        return result;
    }

    // ── Test Grading: client-side evaluation (mirrors _evaluate_response) ──

    function evaluateTestResponse(data, config, weight) {
        // Path 1: JS-provided correct boolean
        if ('correct' in data && typeof data.correct === 'boolean') {
            var isCorrect = data.correct;
            return {
                isCorrect: isCorrect,
                score: isCorrect ? weight : 0.0,
                feedback: data.feedback || (
                    isCorrect
                        ? (config.correct_feedback || 'Correct!')
                        : (config.incorrect_feedback || 'Incorrect. Try again.')
                )
            };
        }

        // Path 2: no config
        if (!config || Object.keys(config).length === 0) {
            return { isCorrect: false, score: 0.0, feedback: 'No grading configuration.' };
        }

        // Path 3a: single answer match
        if ('answer' in data && 'answer' in config) {
            var userAnswer = String(data.answer).trim().toLowerCase();
            var correctAnswer = String(config.answer).trim().toLowerCase();
            var correct = userAnswer === correctAnswer;
            return {
                isCorrect: correct,
                score: correct ? weight : 0.0,
                feedback: correct
                    ? (config.correct_feedback || 'Correct!')
                    : (config.incorrect_feedback || 'Incorrect. Try again.')
            };
        }

        // Path 3b: multi-field match
        if (config.fields && typeof config.fields === 'object') {
            var totalFields = Object.keys(config.fields).length;
            var correctFields = 0;
            for (var fieldName in config.fields) {
                if (fieldName in data) {
                    var userVal = String(data[fieldName]).trim().toLowerCase();
                    var expected = String(config.fields[fieldName]).trim().toLowerCase();
                    if (userVal === expected) correctFields++;
                }
            }
            var allCorrect = correctFields === totalFields;
            var score = totalFields > 0 ? (correctFields / totalFields) * weight : 0.0;
            return {
                isCorrect: allCorrect,
                score: Math.round(score * 100) / 100,
                feedback: allCorrect
                    ? (config.correct_feedback || 'All answers correct!')
                    : (config.incorrect_feedback || correctFields + '/' + totalFields + ' answers correct.'),
                correctFields: correctFields,
                totalFields: totalFields
            };
        }

        return { isCorrect: false, score: 0.0, feedback: 'No matching answer fields found.' };
    }

    // ── Test Grading: update test inputs based on current mode ──

    function updateTestInputs() {
        var container = $(element).find('#test-grading-inputs');
        var mode = $(element).find('#xb_grading_mode').val();
        var autoGrade = $(element).find('#xb_auto_grade_enabled').val() === '1';
        container.empty();

        // Hide result when inputs change
        $(element).find('#test-grading-result').hide();

        if (!autoGrade || mode === 'none') {
            container.append(
                '<div style="margin-bottom: 4px;">' +
                  '<label class="label setting-label" style="font-size:0.85em;">Test JSON payload</label>' +
                  '<textarea class="input setting-input test-json-input" rows="3" ' +
                    'placeholder=\'{"answer": "4", "correct": true}\'></textarea>' +
                '</div>'
            );
        } else if (mode === 'single') {
            container.append(
                '<div style="margin-bottom: 4px;">' +
                  '<label class="label setting-label" style="font-size:0.85em;">Test Answer</label>' +
                  '<input class="input setting-input test-single-input" type="text" placeholder="Type a test answer..." />' +
                '</div>'
            );
        } else if (mode === 'multi') {
            $(element).find('.grading-field-row').each(function() {
                var fieldName = $(this).find('.grading-field-name').val().trim();
                if (fieldName) {
                    container.append(
                        '<div style="display:flex;gap:8px;margin-bottom:4px;align-items:center;">' +
                          '<label class="label setting-label" style="font-size:0.85em;min-width:120px;margin:0;">' + fieldName + '</label>' +
                          '<input class="input setting-input test-multi-input" type="text" data-field="' + fieldName + '" placeholder="Test value..." style="flex:1;" />' +
                        '</div>'
                    );
                }
            });
            if (container.children().length === 0) {
                container.append('<span class="tip setting-help">Add answer fields above first.</span>');
            }
        }
    }

    // ── Test Grading: run test ──

    $(element).find('#test-grading-btn').on('click', function(e) {
        e.preventDefault();
        var mode = $(element).find('#xb_grading_mode').val();
        var autoGrade = $(element).find('#xb_auto_grade_enabled').val() === '1';
        var weight = parseInt($(element).find('input[name=xb_weight]').val()) || 1;
        var config = buildCorrectAnswersJSON();
        var data = {};

        if (!autoGrade || mode === 'none') {
            // Parse JSON from textarea
            var raw = $(element).find('.test-json-input').val().trim();
            if (!raw) {
                showTestResult(null, 'Please enter a test JSON payload.');
                return;
            }
            try {
                data = JSON.parse(raw);
            } catch (err) {
                showTestResult(null, 'Invalid JSON: ' + err.message);
                return;
            }
        } else if (mode === 'single') {
            var val = $(element).find('.test-single-input').val();
            if (val === undefined || val.trim() === '') {
                showTestResult(null, 'Please enter a test answer.');
                return;
            }
            data = { answer: val.trim() };
        } else if (mode === 'multi') {
            $(element).find('.test-multi-input').each(function() {
                var field = $(this).data('field');
                if (field) data[field] = $(this).val().trim();
            });
        }

        var result = evaluateTestResponse(data, config, weight);
        showTestResult(result, null);
    });

    function showTestResult(result, errorMsg) {
        var container = $(element).find('#test-grading-result');

        if (errorMsg) {
            container.css({ background: '#fff3cd', border: '1px solid #ffc107', color: '#856404' });
            container.html('<strong>Error:</strong> ' + errorMsg);
            container.show();
            return;
        }

        var bg = result.isCorrect ? '#d4edda' : '#f8d7da';
        var border = result.isCorrect ? '#28a745' : '#dc3545';
        var color = result.isCorrect ? '#155724' : '#721c24';
        var icon = result.isCorrect ? '\u2713' : '\u2717';
        var status = result.isCorrect ? 'Correct' : 'Incorrect';

        var html = '<div style="margin-bottom:6px;">' +
            '<strong style="font-size:1.1em;">' + icon + ' ' + status + '</strong>' +
            '</div>' +
            '<div>Score: <strong>' + result.score + ' / ' + (parseInt($(element).find('input[name=xb_weight]').val()) || 1) + '</strong></div>';

        if (result.totalFields !== undefined) {
            html += '<div>Fields: ' + result.correctFields + ' / ' + result.totalFields + ' correct</div>';
        }

        if (result.feedback) {
            html += '<div style="margin-top:6px;">Feedback: <em>' + result.feedback + '</em></div>';
        }

        container.css({ background: bg, border: '1px solid ' + border, color: color });
        container.html(html);
        container.show();
    }

    // ── Save handler ──

    $(element).find('.save-button').bind('click', function() {
        var formData = {
            display_name: $(element).find('input[name=xb_display_name]').val(),
            html_content: $(element).find('textarea[name=xb_html_content]').val(),
            css_content: $(element).find('textarea[name=xb_css_content]').val(),
            js_content: $(element).find('textarea[name=xb_js_content]').val(),
            weight: parseInt($(element).find('input[name=xb_weight]').val()) || 1,
            enable_debug_mode: $(element).find('#xb_enable_debug_mode').val() === '1',
            auto_grade_enabled: $(element).find('#xb_auto_grade_enabled').val() === '1',
            correct_answers: buildCorrectAnswersJSON(),
            show_feedback_to_learners: $(element).find('#xb_show_feedback_to_learners').val() === '1',
            show_previous_response: $(element).find('#xb_show_previous_response').val() === '1'
        };

        // Validate required fields
        if (!formData.html_content.trim()) {
            alert('HTML content cannot be empty');
            return;
        }

        // Validate grading config when auto-grade is enabled
        if (formData.auto_grade_enabled) {
            var mode = $(element).find('#xb_grading_mode').val();
            if (mode === 'single' && !$(element).find('#xb_single_answer').val().trim()) {
                alert('Please enter a correct answer or switch mode to "None".');
                return;
            }
            if (mode === 'multi') {
                var hasFields = $(element).find('.grading-field-row .grading-field-name')
                    .filter(function() { return $(this).val().trim() !== ''; }).length > 0;
                if (!hasFields) {
                    alert('Please add at least one answer field or switch to a different mode.');
                    return;
                }
            }
        }

        // Show loading state
        var saveButton = $(element).find('.save-button');
        var originalText = saveButton.text();
        saveButton.text('Saving...').prop('disabled', true);

        if ('notify' in runtime) {
            runtime.notify('save', { state: 'start' });
        }

        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(formData),
            contentType: "application/json",
            success: function(response) {
                saveButton.text(originalText).prop('disabled', false);
                if ('notify' in runtime) {
                    runtime.notify('save', { state: 'end' });
                }
            },
            error: function(xhr, status, error) {
                saveButton.text(originalText).prop('disabled', false);
                alert('Failed to save block: ' + error);
            }
        });
    });

    $(element).find('.cancel-button').bind('click', function() {
        if ('notify' in runtime) {
            runtime.notify('cancel', {});
        }
    });
}
