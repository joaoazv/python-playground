"""
Unit tests for the Chatbot class in the chatbot application.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Adjust sys.path to allow imports from the chatbot_project
# This assumes this test script is in `some_path/chatbot_project/tests/test_chatbot.py`
# We want `some_path` to be in `sys.path` for `from chatbot_project.main...`
try:
    from chatbot_project.main import Chatbot
    from chatbot_project.config import settings # For settings.CHATBOT_NAME
    # We don't need actual task classes here, they will be mocked.
except ImportError:
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_parent = os.path.abspath(os.path.join(current_file_dir, '..', '..'))
    if project_root_parent not in sys.path:
        sys.path.insert(0, project_root_parent)
    from chatbot_project.main import Chatbot
    from chatbot_project.config import settings


class TestChatbot(unittest.TestCase):

    def setUp(self):
        """
        Set up for test methods.
        This will involve creating a Chatbot instance and mocking the task classes
        that are normally stored in chatbot.tasks.
        """
        # We need to patch where the tasks are LOOKED UP by main.Chatbot
        # which is in the `chatbot_project.main` module's namespace.
        # So, when Chatbot() is called, it populates self.tasks with these patched versions.
        
        # Define mock classes for each task
        self.mock_api_task_class = MagicMock(name="MockAPITaskClass")
        self.mock_search_file_task_class = MagicMock(name="MockSearchFileTaskClass")
        self.mock_search_text_task_class = MagicMock(name="MockSearchTextTaskClass")

        # Configure the .return_value for each mock class to simulate instance creation
        # Each instance needs an 'execute' method which is also a mock
        self.mock_api_task_instance = self.mock_api_task_class.return_value
        self.mock_search_file_task_instance = self.mock_search_file_task_class.return_value
        self.mock_search_text_task_instance = self.mock_search_text_task_class.return_value
        
        # Patch the task classes in the module where Chatbot is defined and imports them
        # This ensures that when Chatbot initializes self.tasks, it uses our mocks.
        self.patches = {
            'chatbot_project.main.APITask': self.mock_api_task_class,
            'chatbot_project.main.SearchFileTask': self.mock_search_file_task_class,
            'chatbot_project.main.SearchTextTask': self.mock_search_text_task_class,
        }
        
        # Apply all patches
        self.patchers = [patch(target, mock_class) for target, mock_class in self.patches.items()]
        for p in self.patchers:
            p.start()
            self.addCleanup(p.stop) # Ensure patches are stopped after each test

        self.chatbot = Chatbot()


    def test_handle_input_known_command_api_task(self):
        expected_response = "API Task Result for user 123"
        self.mock_api_task_instance.execute.return_value = expected_response
        
        query = "123"
        user_input = f"search_user {query}"
        response = self.chatbot.handle_input(user_input)

        self.mock_api_task_class.assert_called_once_with() # Assert class was instantiated
        self.mock_api_task_instance.execute.assert_called_once_with(query)
        self.assertEqual(response, expected_response)

    def test_handle_input_known_command_find_file_task(self):
        expected_response = "File Task Result for test.txt in /path"
        self.mock_search_file_task_instance.execute.return_value = expected_response
        
        query = "test.txt in /path"
        user_input = f"find_file {query}"
        response = self.chatbot.handle_input(user_input)

        self.mock_search_file_task_class.assert_called_once_with()
        self.mock_search_file_task_instance.execute.assert_called_once_with(query)
        self.assertEqual(response, expected_response)

    def test_handle_input_known_command_search_text_task(self):
        expected_response = "Text Search Result for 'hello' in /path"
        self.mock_search_text_task_instance.execute.return_value = expected_response
        
        query = "'hello' in /path" # Query includes the quotes for this task
        user_input = f"search_text {query}"
        response = self.chatbot.handle_input(user_input)

        self.mock_search_text_task_class.assert_called_once_with()
        self.mock_search_text_task_instance.execute.assert_called_once_with(query)
        self.assertEqual(response, expected_response)

    def test_handle_input_unknown_command(self):
        user_input = "unknown_command query"
        response = self.chatbot.handle_input(user_input)
        
        self.assertIn("Unknown command 'unknown_command'", response)
        self.mock_api_task_instance.execute.assert_not_called()
        self.mock_search_file_task_instance.execute.assert_not_called()
        self.mock_search_text_task_instance.execute.assert_not_called()

    def test_handle_input_command_with_no_query_search_user(self):
        # search_user task requires a query (user ID)
        response = self.chatbot.handle_input("search_user")
        self.assertIn("Error: Please provide a user ID.", response)
        self.mock_api_task_instance.execute.assert_not_called()

    def test_handle_input_command_with_no_query_find_file(self):
        # find_file task requires a query (filename)
        response = self.chatbot.handle_input("find_file")
        self.assertIn("Error: Please provide a filename.", response)
        self.mock_search_file_task_instance.execute.assert_not_called()

    def test_handle_input_command_with_no_query_search_text(self):
        # search_text task requires a query (text and directory)
        response = self.chatbot.handle_input("search_text")
        self.assertIn("Error: Please provide search text and directory.", response)
        self.mock_search_text_task_instance.execute.assert_not_called()

    def test_handle_input_quit_command_is_unknown_to_handler(self):
        # The 'quit' command is handled by the run loop, not handle_input.
        response = self.chatbot.handle_input("quit")
        self.assertIn("Unknown command 'quit'", response)

    @patch('builtins.input', side_effect=['search_user 1', 'quit'])
    @patch('builtins.print')
    def test_run_loop_welcome_and_goodbye(self, mock_print, mock_input):
        self.mock_api_task_instance.execute.return_value = "User 1 data"
        
        self.chatbot.run()

        # Check welcome message
        mock_print.assert_any_call(f"Welcome to {settings.CHATBOT_NAME}! Type 'quit' to exit.")
        
        # Check that print was called for the task response
        mock_print.assert_any_call(f"{settings.CHATBOT_NAME}: User 1 data")
        
        # Check goodbye message
        mock_print.assert_any_call(f"Goodbye from {settings.CHATBOT_NAME}!")
        
        # Ensure execute was called for the command
        self.mock_api_task_instance.execute.assert_called_once_with("1")


    @patch('builtins.input', side_effect=['invalid_command', 'quit'])
    @patch('builtins.print')
    def test_run_loop_handles_invalid_command_gracefully(self, mock_print, mock_input):
        self.chatbot.run()

        mock_print.assert_any_call(f"Welcome to {settings.CHATBOT_NAME}! Type 'quit' to exit.")
        
        # Check that the unknown command response was printed
        expected_unknown_msg_fragment = "Unknown command 'invalid_command'"
        
        # Iterate through print calls to find the relevant one
        found_unknown_command_response = False
        for call_args in mock_print.call_args_list:
            if expected_unknown_msg_fragment in call_args[0][0]:
                found_unknown_command_response = True
                break
        self.assertTrue(found_unknown_command_response, "Did not print unknown command message.")

        mock_print.assert_any_call(f"Goodbye from {settings.CHATBOT_NAME}!")


if __name__ == '__main__':
    # Ensure the path is set for `from chatbot_project.main...` type imports
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_parent = os.path.abspath(os.path.join(current_file_dir, '..', '..'))
    if project_root_parent not in sys.path:
        sys.path.insert(0, project_root_parent)
        
    unittest.main()
