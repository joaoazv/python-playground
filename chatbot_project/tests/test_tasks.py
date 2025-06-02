"""
Unit tests for the task classes in the chatbot application.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import shutil
import tempfile
import requests # For requests.exceptions.RequestException

# Add the project root (parent directory of 'tests' and 'chatbot_project') to sys.path
# This allows imports like `from chatbot_project.tasks...`
# This assumes the script is in chatbot_project/tests/test_tasks.py
# and the modules to test are in chatbot_project/tasks/
#
# Project structure:
# parent_dir/
#   chatbot_project/
#     __init__.py (optional, but good practice for package)
#     tasks/
#       __init__.py
#       base_task.py
#       example_task_api.py
#     tests/
#       __init__.py
#       test_tasks.py
#
# When running `python test_tasks.py` from `chatbot_project/tests/`,
# `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` should give `parent_dir`.
# No, it will give `chatbot_project`.
# We need `chatbot_project`'s parent on the path to do `from chatbot_project.tasks...`
# Or, if `chatbot_project` is the CWD, then `from tasks...` should work.

# Let's assume the tests will be run from the parent directory of `chatbot_project`
# e.g., `python -m unittest chatbot_project.tests.test_tasks`
# Or from `chatbot_project` root: `python -m unittest tests.test_tasks`
# In these cases, Python's test discovery and path handling should work.
# If running `python test_tasks.py` directly from `chatbot_project/tests/`,
# we need to adjust sys.path to find `chatbot_project` as a package.

# current_dir = os.path.dirname(os.path.abspath(__file__)) # .../chatbot_project/tests
# project_root_for_imports = os.path.dirname(current_dir) # .../chatbot_project
# # To do `from chatbot_project.tasks...` we need parent of project_root_for_imports in path
# parent_of_project_root = os.path.dirname(project_root_for_imports)


# Simplified sys.path adjustment: Add the 'chatbot_project' directory itself
# to sys.path, assuming it contains `tasks`, `config` etc. as sub-packages/modules.
# This is if we are running the test script directly from `chatbot_project/tests`.
# This assumes that 'chatbot_project' is the top-level package we want to import from.
# To do `from tasks...` or `from config...` directly, `chatbot_project` dir needs to be in sys.path.
# To do `from chatbot_project.tasks...`, the parent of `chatbot_project` needs to be in sys.path.

# Let's try to make it work by running `python -m unittest discover` from `chatbot_project` parent,
# or `python -m unittest tests.test_tasks` from `chatbot_project`.
# For the tool environment, it's usually safest to add the project's parent dir to sys.path.
# This makes `from chatbot_project.tasks...` robust.
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
# SCRIPT_DIR is now /app/chatbot_project/tests if tool runs from /app
# To import `from chatbot_project.tasks...`, /app needs to be in sys.path
# sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT, PACKAGE_PARENT)))
# This would be /app/chatbot_project/tests/../../ -> /app
# Let's assume the testing environment or execution command handles PYTHONPATH.
# If direct execution `python chatbot_project/tests/test_tasks.py` is needed,
# then `chatbot_project`'s parent must be in `sys.path`.
# For now, I will use `from chatbot_project.tasks...` and assume the path is set up by the environment.
# The `run_in_bash_session` tool will likely run from `/app` (parent of `chatbot_project`)

# If running `python -m unittest discover` from `/app`, then `chatbot_project` is a top-level package.
# So, `from chatbot_project.tasks.example_task_api import APITask` should work.

try:
    from chatbot_project.tasks.example_task_api import APITask
    from chatbot_project.tasks.example_task_search_file import SearchFileTask
    from chatbot_project.tasks.example_task_search_text import SearchTextTask
except ImportError:
    # Fallback for environments where chatbot_project's parent isn't in PYTHONPATH
    # This is common when running a script directly inside a subfolder.
    # Add parent of chatbot_project (e.g. /app if structure is /app/chatbot_project)
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from chatbot_project.tasks.example_task_api import APITask
    from chatbot_project.tasks.example_task_search_file import SearchFileTask
    from chatbot_project.tasks.example_task_search_text import SearchTextTask


class TestAPITask(unittest.TestCase):

    @patch('chatbot_project.tasks.example_task_api.requests.get')
    def test_execute_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1, 
            "name": "Test User", 
            "email": "test@example.com", 
            "company": {"name": "Test Inc"}
        }
        mock_get.return_value = mock_response

        task = APITask()
        result = task.execute("1")
        
        self.assertIn("Test User", result)
        self.assertIn("test@example.com", result)
        self.assertIn("Test Inc", result)
        mock_get.assert_called_once_with("https://jsonplaceholder.typicode.com/users/1")

    @patch('chatbot_project.tasks.example_task_api.requests.get')
    def test_execute_failure_network_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        task = APITask()
        result = task.execute("1")
        
        self.assertIn("Error: API request failed", result)
        self.assertIn("Network error", result)

    @patch('chatbot_project.tasks.example_task_api.requests.get')
    def test_execute_failure_http_error_404(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Client Error: Not Found for url", response=mock_response
        )
        mock_get.return_value = mock_response
        
        task = APITask()
        result = task.execute("999") # Non-existent user
        
        self.assertIn("Error: User with ID '999' not found (404)", result)

    @patch('chatbot_project.tasks.example_task_api.requests.get')
    def test_execute_failure_http_error_500(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        # Configure raise_for_status to be called and raise the HTTPError
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "500 Server Error", response=mock_response
        )
        mock_get.return_value = mock_response
        
        task = APITask()
        result = task.execute("1")
        
        self.assertIn("HTTP error occurred", result)
        self.assertIn("Status code: 500", result)

    def test_execute_invalid_user_id(self):
        task = APITask()
        result = task.execute("abc")
        self.assertIn("Invalid user ID provided", result)
        result = task.execute("-1")
        self.assertIn("Invalid user ID provided", result)
        result = task.execute("0")
        self.assertIn("Invalid user ID provided", result)


class TestSearchFileTask(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        # Create a unique subdirectory for this test to avoid conflicts if CWD is temp_dir
        self.search_base_dir = os.path.join(self.temp_dir, "search_area")
        os.makedirs(self.search_base_dir, exist_ok=True)
        
        self.test_file_name = "test_doc.txt"
        self.test_file_path = os.path.join(self.search_base_dir, self.test_file_name)
        with open(self.test_file_path, "w") as f:
            f.write("This is a test document.")
        
        # Create another file with the same name in a subdirectory
        self.subdir = os.path.join(self.search_base_dir, "subdir")
        os.makedirs(self.subdir, exist_ok=True)
        self.test_file_in_subdir_path = os.path.join(self.subdir, self.test_file_name)
        with open(self.test_file_in_subdir_path, "w") as f:
            f.write("Another test document in a subdirectory.")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_find_file_success_with_specific_path(self):
        task = SearchFileTask()
        result = task.execute(f"{self.test_file_name} in {self.search_base_dir}")
        self.assertIn(f"Files found:", result, "Should indicate multiple files were found")
        self.assertIn(self.test_file_path, result)
        self.assertIn(self.test_file_in_subdir_path, result)

    def test_find_file_success_in_subdir_explicitly(self):
        task = SearchFileTask()
        result = task.execute(f"{self.test_file_name} in {self.subdir}")
        self.assertIn(f"File found: {self.test_file_in_subdir_path}", result)


    def test_find_file_success_simple_name_within_mocked_getcwd(self):
        task = SearchFileTask()
        # Mock os.getcwd() to return our specific search base directory
        with patch('chatbot_project.tasks.example_task_search_file.os.getcwd', return_value=self.search_base_dir):
            result = task.execute(self.test_file_name) # Query is just "test_doc.txt"
        
        # Depending on os.walk order, either can be first if multiple are found.
        # The task returns "Files found:\npath1\npath2" if multiple.
        self.assertTrue(self.test_file_path in result and self.test_file_in_subdir_path in result)
        self.assertIn("Files found:", result)


    def test_find_file_not_found(self):
        task = SearchFileTask()
        result = task.execute(f"nonexistent.txt in {self.search_base_dir}")
        self.assertIn(f"File 'nonexistent.txt' not found in '{self.search_base_dir}'", result)

    def test_find_file_invalid_directory(self):
        task = SearchFileTask()
        invalid_path = "/invalid/path/that/does/not/exist"
        result = task.execute(f"{self.test_file_name} in {invalid_path}")
        self.assertIn(f"Error: Invalid search directory '{invalid_path}'", result)
    
    def test_find_file_empty_filename(self):
        task = SearchFileTask()
        result = task.execute(f" in {self.search_base_dir}")
        self.assertIn("Error: Invalid query format. Filename cannot be empty.", result)


class TestSearchTextTask(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.file1_path = os.path.join(self.temp_dir, "file1.txt")
        self.file2_path = os.path.join(self.temp_dir, "file2.py")
        self.subdir = os.path.join(self.temp_dir, "sub")
        os.makedirs(self.subdir)
        self.file3_path = os.path.join(self.subdir, "file3.log")
        self.binary_file_path = os.path.join(self.temp_dir, "binary.dat")

        with open(self.file1_path, "w", encoding="utf-8") as f:
            f.write("Hello world, this is a test.\nPython programming is fun.\nAnother line with Hello world.")
        with open(self.file2_path, "w", encoding="utf-8") as f:
            f.write("# Python comment\ndef greet():\n    print('Hello python') # A greeting")
        with open(self.file3_path, "w", encoding="utf-8") as f:
            f.write("Log entry: Hello world again.")
        with open(self.binary_file_path, "wb") as f:
            f.write(b"\x00\x01\xfa\xba\xdd\xee\x00")


    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_search_text_found_multiple_occurrences_and_files(self):
        task = SearchTextTask()
        result = task.execute(f"'Hello world' in {self.temp_dir}")
        self.assertIn(f"Search text 'Hello world' found in:", result)
        self.assertIn(f"- {self.file1_path} (Lines: 1, 3)", result)
        self.assertIn(f"- {self.file3_path} (Lines: 1)", result) # from subdir
        self.assertNotIn(self.file2_path, result) # "Hello python" is different
        self.assertIn(f"{self.binary_file_path} (Reason: UnicodeDecodeError)", result)


    def test_search_text_found_one_file_specific_text(self):
        task = SearchTextTask()
        result = task.execute(f"'Python programming' in {self.temp_dir}")
        self.assertIn(f"Search text 'Python programming' found in:", result)
        self.assertIn(f"- {self.file1_path} (Lines: 2)", result)
        self.assertNotIn(self.file2_path, result)
        self.assertNotIn(self.file3_path, result)

    def test_search_text_not_found(self):
        task = SearchTextTask()
        result = task.execute(f"'unique_text_not_present_ever' in {self.temp_dir}")
        self.assertIn(f"Search text 'unique_text_not_present_ever' not found in '{self.temp_dir}'.", result)
        self.assertIn(f"{self.binary_file_path} (Reason: UnicodeDecodeError)", result) # Still reports unreadable

    def test_search_text_invalid_directory(self):
        task = SearchTextTask()
        invalid_path = "/totally/invalid/path/for/search"
        result = task.execute(f"'any text' in {invalid_path}")
        self.assertIn(f"Error: Invalid search directory '{invalid_path}'.", result)

    def test_search_text_invalid_query_format(self):
        task = SearchTextTask()
        self.assertIn("Error: Invalid query format.", task.execute("just text no dir"))
        self.assertIn("Error: Invalid query format.", task.execute("text' in directory")) # Missing opening quote
        self.assertIn("Error: Invalid query format.", task.execute("'text in directory")) # Missing closing quote
        self.assertIn("Error: Search text cannot be empty.", task.execute(f"'' in {self.temp_dir}"))

    def test_search_text_in_binary_file_only(self):
        task = SearchTextTask()
        # Create a new temp dir with only the binary file to simplify the test
        temp_binary_dir = tempfile.mkdtemp()
        binary_file = os.path.join(temp_binary_dir, "only_binary.bin")
        with open(binary_file, "wb") as f:
            f.write(b"\x80\x81\x82") # Some binary data
        
        result = task.execute(f"'some text' in {temp_binary_dir}")
        self.assertIn(f"Search text 'some text' not found in '{temp_binary_dir}'.", result)
        self.assertIn(f"{binary_file} (Reason: UnicodeDecodeError)", result)
        
        shutil.rmtree(temp_binary_dir)


if __name__ == '__main__':
    # This allows running the tests directly from this file:
    # `python chatbot_project/tests/test_tasks.py`
    # For this to work, the sys.path manipulation at the top might be crucial
    # if `chatbot_project`'s parent isn't already in PYTHONPATH.
    # A more standard way is to run `python -m unittest discover` from project root's parent,
    # or `python -m unittest tests.test_tasks` from project root.
    
    # If the ImportError try/except block at the top worked, this should be fine.
    # Let's ensure the path is set for `from chatbot_project.tasks...` type imports
    # This assumes this test script is in `some_path/chatbot_project/tests/test_tasks.py`
    # We want `some_path` to be in `sys.path`
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_parent = os.path.abspath(os.path.join(current_file_dir, '..', '..'))
    if project_root_parent not in sys.path:
        sys.path.insert(0, project_root_parent)
        
    unittest.main()
