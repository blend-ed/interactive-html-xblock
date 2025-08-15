# InteractiveJSBlock Enhanced Features

This document describes the enhanced features added to the InteractiveJSBlock to support learner feedback, correct/incorrect responses, and staff visibility.

## New Features

### 1. Learner Feedback and Scoring

#### Auto-Grading System
- **Correct Answers Configuration**: Define correct answers in JSON format in the studio
- **Automatic Evaluation**: Responses are automatically evaluated against correct answers
- **Score Calculation**: Automatic score calculation based on weight and correctness
- **Feedback Messages**: Customizable feedback messages for correct/incorrect responses

#### Example Correct Answers Configuration:
```json
{
  "answer": "4",
  "correct_feedback": "Great job! That's correct.",
  "incorrect_feedback": "Try again. The answer is 4."
}
```

For multiple fields:
```json
{
  "fields": {
    "question1": "yes",
    "question2": "no"
  },
  "correct_feedback": "All answers correct!",
  "incorrect_feedback": "Some answers are incorrect."
}
```

### 2. Learner Experience Enhancements

#### Previous Response Display
- **Show Previous Response**: Learners can see their previous responses when they return
- **Response History**: Complete interaction history is preserved
- **Feedback Display**: Shows correct/incorrect status and scores

#### Real-time Feedback
- **Immediate Feedback**: Feedback is shown immediately after interaction
- **Score Display**: Current score is displayed
- **Status Indicators**: Visual indicators for correct/incorrect responses

### 3. Staff Visibility

#### Student View for Staff
- **Staff Panel**: Special panel visible only to staff users
- **Real-time Data**: Live interaction data and statistics
- **Learner Response View**: Complete view of learner responses

#### Instructor Dashboard Integration
- **Course-wide View**: View all InteractiveJSBlock interactions across the course
- **Statistics**: Summary statistics for each block
- **Student Responses**: Detailed view of individual student responses
- **Success Rates**: Calculate and display success rates

### 4. Configuration Options

#### Studio Settings
- **Auto Grade Enabled**: Toggle automatic grading
- **Show Feedback to Learners**: Control whether learners see feedback
- **Show Previous Response**: Control whether previous responses are shown
- **Enable Instructor View**: Control instructor dashboard visibility
- **Weight**: Set the weight for grading purposes

## Usage Examples

### Basic Interactive Quiz
```html
<div class="quiz">
  <h3>What is 2 + 2?</h3>
  <input type="number" id="answer" />
  <button onclick="submitAnswer()">Submit</button>
</div>

<script>
function submitAnswer() {
  var answer = document.getElementById('answer').value;
  submitInteraction({
    answer: answer,
    question: 'addition',
    timestamp: new Date().toISOString()
  });
}
</script>
```

### Complex Interactive Exercise
```html
<div class="exercise">
  <h3>Complete the form</h3>
  <input type="text" id="name" placeholder="Your name" />
  <input type="email" id="email" placeholder="Your email" />
  <button onclick="submitForm()">Submit</button>
</div>

<script>
function submitForm() {
  var name = document.getElementById('name').value;
  var email = document.getElementById('email').value;
  
  submitInteraction({
    name: name,
    email: email,
    completed: true,
    timeSpent: calculateTimeSpent()
  });
}
</script>
```

## Instructor Dashboard Setup

To enable the instructor dashboard, add the following to your Open edX settings:

```python
FEATURES["ENABLE_INTERACTIVE_JS_INSTRUCTOR_VIEW"] = True
OPEN_EDX_FILTERS_CONFIG = {
    "org.openedx.learning.instructor.dashboard.render.started.v1": {
        "fail_silently": False,
        "pipeline": [
            "interactive_html_xblock.extensions.filters.AddInteractiveJSTab",
        ]
    },
}
```

## Technical Implementation

### Data Storage
- **Learner Response**: Stored in user state scope
- **Interaction Count**: Tracks number of interactions
- **Score**: Stored as float value
- **Correctness**: Boolean flag for correct/incorrect
- **Feedback Message**: String message for learner

### JavaScript Integration
- **submitInteraction()**: Global function for sending data
- **Runtime Integration**: Proper XBlock runtime integration
- **Error Handling**: Comprehensive error handling and logging

### Security Features
- **Input Validation**: JSON validation for correct answers
- **Access Control**: Staff-only access to instructor views
- **Data Sanitization**: Proper data sanitization and validation

## Migration from Previous Version

The enhanced features are backward compatible. Existing blocks will continue to work without modification. New features are opt-in and can be enabled through studio settings.

## Troubleshooting

### Common Issues

1. **Runtime Not Available Error**
   - Ensure the XBlock is properly initialized
   - Check that the JavaScript is loading correctly

2. **Feedback Not Showing**
   - Verify "Show Feedback to Learners" is enabled
   - Check that auto-grading is configured correctly

3. **Instructor Dashboard Not Visible**
   - Ensure the feature flag is enabled
   - Check that the filter is properly configured

### Debug Mode
Enable debug mode in studio settings to see detailed information about:
- Current response data
- Interaction counts
- Score calculations
- Error messages

## Future Enhancements

Planned features for future releases:
- Advanced grading algorithms
- Peer review integration
- Analytics dashboard
- Export functionality
- Mobile optimization
