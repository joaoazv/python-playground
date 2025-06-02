"""
Main application file for the TaskBot.
This file defines the Chatbot class and handles the main interaction loop.
"""

import sys
import os

# Ensure the project root is in the Python path
# This allows for `from tasks...` or `from config...` imports
# when running main.py directly from within the chatbot_project directory
# or when chatbot_project is the CWD.
if os.getcwd().endswith("chatbot_project"):
    # If CWD is chatbot_project, its parent needs to be in path for `from chatbot_project...`
    # However, if we are running `python main.py` from *inside* chatbot_project,
    # then relative imports like `from .tasks` or `from tasks` should work if Python adds CWD to path.
    # Let's adjust for running `python chatbot_project/main.py` from the parent of chatbot_project,
    # or if chatbot_project itself is a package used elsewhere.
    # For simplicity, if chatbot_project is the CWD, direct imports like `from tasks...` should be fine.
    pass # Assume Python's default path handling is sufficient if CWD is chatbot_project
else:
    # If script is run from parent dir (e.g. python chatbot_project/main.py)
    # or if chatbot_project is not the CWD, add current file's dir to allow relative import of siblings
    # This is a bit tricky. The most robust way for development is often setting PYTHONPATH
    # or using a virtual environment where the package is installed in editable mode.
    # For this specific structure, if we run `python main.py` from `chatbot_project`,
    # imports like `from tasks...` are standard.
    # If we run `python chatbot_project/main.py` from the *parent* of `chatbot_project`,
    # then `chatbot_project` itself acts like a package name.

    # Simplest approach for now: if this script is chatbot_project/main.py,
    # and we want to run it from *outside* chatbot_project, then chatbot_project's parent
    # should be in sys.path so `from chatbot_project.tasks...` works.
    # If we run it *from* chatbot_project, `from tasks...` works.
    # Let's assume we are running it from within chatbot_project folder for now.
    # If not, the user would need to set PYTHONPATH or install the package.
    pass


# Use relative imports as main.py is part of the chatbot_project package.
# This assumes the script is run as a module (e.g. python -m chatbot_project.main)
# or that the parent directory of chatbot_project is in sys.path.
# For direct execution `python main.py` from within `chatbot_project` directory,
# Python adds the script's directory to sys.path, allowing these to resolve.
from .tasks.example_task_api import APITask
from .tasks.example_task_search_file import SearchFileTask
from .tasks.example_task_search_text import SearchTextTask
from .config import settings


class Chatbot:
    """
    A simple command-line chatbot that can perform various tasks.
    """
    def __init__(self):
        """
        Initializes the Chatbot with a set of available tasks.
        """
        self.tasks = {
            "search_user": APITask,
            "find_file": SearchFileTask,
            "search_text": SearchTextTask,
        }
        # API key can be passed here if needed by APITask's __init__
        # For example:
        # self.api_task_instance = APITask(api_key=settings.WEATHER_API_KEY)
        # And then in handle_input:
        # if command == "search_user":
        #    task_instance = self.api_task_instance # or a new one if key is per-call
        # else:
        #    task_instance = task_class()

    def handle_input(self, user_input: str) -> str:
        """
        Parses the user input to identify a command and its arguments,
        then executes the corresponding task.

        Args:
            user_input: The raw string input from the user.

        Returns:
            A string containing the result of the task execution or an error message.
        """
        parts = user_input.strip().split(" ", 1)
        command = parts[0].lower()
        query_part = parts[1] if len(parts) > 1 else ""

        if command in self.tasks:
            task_class = self.tasks[command]
            
            # Example of how to pass API key if APITask __init__ required it:
            # if command == "search_user":
            #     # Assuming APITask is designed to take api_key in its constructor
            #     # And that settings.WEATHER_API_KEY is the relevant key
            #     task_instance = task_class(api_key=settings.WEATHER_API_KEY)
            # else:
            #     task_instance = task_class()
            task_instance = task_class() # Current tasks don't need init args from settings

            if not query_part and command in ["search_user", "find_file", "search_text"]:
                 # search_user <id>
                 # find_file <name> [in <path>] -> filename is required
                 # search_text "<text>" in <path> -> text and path are required
                 # A more robust solution would have each task define its expected arg format
                if command == "search_user":
                    return "Error: Please provide a user ID. Usage: search_user <id>"
                elif command == "find_file":
                    return "Error: Please provide a filename. Usage: find_file <filename> [in <directory>]"
                elif command == "search_text":
                    return "Error: Please provide search text and directory. Usage: search_text \"<text>\" in <directory>"
            
            return task_instance.execute(query_part)
        else:
            return (
                f"Unknown command '{command}'. Try one of:\n"
                f"  - search_user <user_id>\n"
                f"  - find_file <filename> [in <directory>]\n"
                f"  - search_text \"<text_to_search>\" in <directory>\n"
                f"  - quit"
            )

    def run(self):
        """
        Starts the main interaction loop for the chatbot.
        """
        print(f"Welcome to {settings.CHATBOT_NAME}! Type 'quit' to exit.")
        while True:
            try:
                user_input = input("You: ")
                if user_input.strip().lower() == "quit":
                    print(f"Goodbye from {settings.CHATBOT_NAME}!")
                    break
                
                response = self.handle_input(user_input)
                print(f"{settings.CHATBOT_NAME}: {response}")
            except KeyboardInterrupt: # Allow Ctrl+C to exit gracefully
                print(f"\nGoodbye from {settings.CHATBOT_NAME}!")
                break
            except EOFError: # Allow Ctrl+D to exit gracefully
                print(f"\nGoodbye from {settings.CHATBOT_NAME}!")
                break


if __name__ == "__main__":
    # This structure assumes that when main.py is run,
    # the Python interpreter can find the 'tasks' and 'config' packages.
    # This is typically true if:
    # 1. You run `python main.py` from within the `chatbot_project` directory.
    # 2. `chatbot_project`'s parent directory is in PYTHONPATH, and you run
    #    `python -m chatbot_project.main`.
    # 3. The `chatbot_project` is installed as a package (e.g., using pip and setup.py).
    
    # The initial import block attempts a simple sys.path modification
    # for common direct script execution scenarios.
    
    bot = Chatbot()
    bot.run()
