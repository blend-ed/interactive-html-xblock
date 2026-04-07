"""
Tests for InteractiveContentXBlock
"""
import unittest
from unittest.mock import Mock, patch

from xblock.test.tools import make_xblock
from xblock.test.scenario import TestScenario

from interactive_content_xblock.xblocks import InteractiveContentXBlock


class TestInteractiveContentXBlock(unittest.TestCase):
    """
    Test cases for InteractiveContentXBlock
    """

    def setUp(self):
        """Set up test fixtures"""
        self.xblock = make_xblock(
            'interactive_content_xblock',
            InteractiveContentXBlock,
            {
                'display_name': 'Test Interactive Block',
                'html_content': '<div>Test HTML</div>',
                'css_content': '.test { color: red; }',
                'js_content': 'console.log("test");',
                'weight': 1,
                'enable_debug_mode': False,
                'auto_grade_enabled': False,
            }
        )

    def test_initialization(self):
        """Test that the XBlock initializes correctly"""
        self.assertEqual(self.xblock.display_name, 'Test Interactive Block')
        self.assertEqual(self.xblock.html_content, '<div>Test HTML</div>')
        self.assertEqual(self.xblock.css_content, '.test { color: red; }')
        self.assertEqual(self.xblock.js_content, 'console.log("test");')
        self.assertEqual(self.xblock.weight, 1)
        self.assertFalse(self.xblock.enable_debug_mode)
        self.assertFalse(self.xblock.auto_grade_enabled)

    def test_max_score(self):
        """Test that max_score returns the correct weight"""
        self.assertEqual(self.xblock.max_score(), 1)

        # Test with different weight
        self.xblock.weight = 5
        self.assertEqual(self.xblock.max_score(), 5)

    def test_student_view(self):
        """Test that student_view renders correctly"""
        fragment = self.xblock.student_view()

        # Check that the fragment contains the expected content
        self.assertIn('<div>Test HTML</div>', fragment.body)
        self.assertIn('.test { color: red; }', fragment.body)
        self.assertIn('console.log("test");', fragment.body)

    def test_studio_view(self):
        """Test that studio_view renders correctly"""
        fragment = self.xblock.studio_view()

        # Check that the fragment contains form elements
        self.assertIn('Display Name', fragment.body)
        self.assertIn('Test Interactive Block', fragment.body)
        self.assertIn('<div>Test HTML</div>', fragment.body)

    def test_save_interaction(self):
        """Test that save_interaction handler works correctly"""
        test_data = {
            'answer': 'test answer',
            'correct': True,
            'timeSpent': 30
        }

        # Mock the runtime
        self.xblock.runtime = Mock()

        # Call the handler
        response = self.xblock.save_interaction(test_data)

        # Check the response
        self.assertEqual(response['status'], 'ok')
        self.assertEqual(response['message'], 'Interaction saved successfully')
        self.assertEqual(response['interaction_count'], 1)

        # Check that the data was saved
        self.assertEqual(self.xblock.learner_response, test_data)
        self.assertEqual(self.xblock.interaction_count, 1)

    def test_save_interaction_invalid_data(self):
        """Test that save_interaction handles invalid data correctly"""
        # Test with non-dict data
        response = self.xblock.save_interaction("not a dict")

        self.assertEqual(response['status'], 'error')
        self.assertEqual(response['message'], 'Data must be a JSON object')

    def test_save_interaction_empty_data(self):
        """Test that save_interaction handles empty data"""
        response = self.xblock.save_interaction({})

        self.assertEqual(response['status'], 'error')
        self.assertEqual(response['message'], 'No data provided')

    def test_save_interaction_emits_completion(self):
        """Test that save_interaction emits completion"""
        self.xblock.runtime = Mock()

        with patch.object(self.xblock, 'emit_completion') as mock_emit:
            self.xblock.save_interaction({'answer': 'test', 'correct': True})
            mock_emit.assert_called_once_with(1.0)

    def test_save_interaction_publishes_grade(self):
        """Test that save_interaction publishes grade when auto-grading is enabled"""
        self.xblock.auto_grade_enabled = True
        self.xblock.weight = 10
        self.xblock.runtime = Mock()

        self.xblock.save_interaction({'answer': 'test', 'correct': True})

        self.xblock.runtime.publish.assert_called_once_with(
            self.xblock,
            'grade',
            {
                'value': 10.0,
                'max_value': 10,
            }
        )

    def test_evaluate_response_correct_field_true(self):
        """Test evaluation when author JS provides correct=True"""
        self.xblock.weight = 5
        self.xblock.runtime = Mock()

        response = self.xblock.save_interaction({'correct': True})

        self.assertEqual(response['is_correct'], True)
        self.assertEqual(response['score'], 5.0)

    def test_evaluate_response_correct_field_false(self):
        """Test evaluation when author JS provides correct=False"""
        self.xblock.weight = 5
        self.xblock.runtime = Mock()

        response = self.xblock.save_interaction({'correct': False})

        self.assertEqual(response['is_correct'], False)
        self.assertEqual(response['score'], 0.0)

    def test_evaluate_response_correct_answers_match(self):
        """Test evaluation with correct_answers config - matching answer"""
        self.xblock.auto_grade_enabled = True
        self.xblock.weight = 10
        self.xblock.correct_answers = {
            'answer': '4',
            'correct_feedback': 'Great!',
            'incorrect_feedback': 'Try again.',
        }
        self.xblock.runtime = Mock()

        response = self.xblock.save_interaction({'answer': '4'})

        self.assertEqual(response['is_correct'], True)
        self.assertEqual(response['score'], 10.0)
        self.assertEqual(response['feedback_message'], 'Great!')

    def test_evaluate_response_correct_answers_mismatch(self):
        """Test evaluation with correct_answers config - wrong answer"""
        self.xblock.auto_grade_enabled = True
        self.xblock.weight = 10
        self.xblock.correct_answers = {
            'answer': '4',
            'correct_feedback': 'Great!',
            'incorrect_feedback': 'Try again.',
        }
        self.xblock.runtime = Mock()

        response = self.xblock.save_interaction({'answer': '5'})

        self.assertEqual(response['is_correct'], False)
        self.assertEqual(response['score'], 0.0)
        self.assertEqual(response['feedback_message'], 'Try again.')

    def test_workbench_scenarios(self):
        """Test that workbench scenarios are defined"""
        scenarios = InteractiveContentXBlock.workbench_scenarios()

        self.assertIsInstance(scenarios, list)
        self.assertGreater(len(scenarios), 0)

        # Check that scenarios have the expected structure
        for title, xml in scenarios:
            self.assertIsInstance(title, str)
            self.assertIsInstance(xml, str)
            self.assertIn('interactive_content_xblock', xml)

    def test_debug_mode_enabled(self):
        """Test that debug mode shows debug information"""
        self.xblock.enable_debug_mode = True
        self.xblock.interaction_count = 5
        self.xblock.last_interaction_time = '2023-01-01T00:00:00Z'

        fragment = self.xblock.student_view()

        # Check that debug information is included
        self.assertIn('Debug Information', fragment.body)
        self.assertIn('5', fragment.body)
        self.assertIn('2023-01-01T00:00:00Z', fragment.body)

    def test_debug_mode_disabled(self):
        """Test that debug mode hides debug information when disabled"""
        self.xblock.enable_debug_mode = False

        fragment = self.xblock.student_view()

        # Check that debug information is not included
        self.assertNotIn('Debug Information', fragment.body)


if __name__ == '__main__':
    unittest.main()
