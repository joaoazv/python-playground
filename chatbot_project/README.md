# AI Conversational TaskBot

## Overview

This project is a command-line based AI conversational chatbot named "TaskBot". Its primary purpose is to automate various tasks through simple conversational commands. It is designed with an extensible architecture, allowing developers to easily add new functionalities (tasks) to enhance its capabilities.

## Features

Currently, TaskBot supports the following example tasks:

*   **Search User**: Fetches user details (name, email, company) from the JSONPlaceholder API using a user ID.
*   **Find File**: Searches for a specified file within a given directory (or the current working directory if no path is provided).
*   **Search Text in Files**: Searches for a given text string within all files in a specified directory, reporting the files and line numbers where the text is found.

The chatbot is designed to be easily extended with new custom tasks.

## Project Structure

The project is organized into the following main directories and files:

*   `chatbot_project/`: The root directory for the chatbot application.
    *   `main.py`: The main entry point for the chatbot application. It contains the `Chatbot` class and the primary interaction loop.
    *   `tasks/`: Contains the task definitions.
        *   `base_task.py`: Defines the abstract `Task` base class that all tasks must inherit from.
        *   `example_task_api.py`: Implements `APITask` for fetching user data.
        *   `example_task_search_file.py`: Implements `SearchFileTask` for finding files.
        *   `example_task_search_text.py`: Implements `SearchTextTask` for searching text in files.
    *   `config/`: Holds configuration files.
        *   `settings.py`: Contains application settings like API keys and default paths.
    *   `utils/`: Includes utility functions and helper modules.
        *   `helpers.py`: Currently includes `make_api_request` for making generic API calls.
    *   `tests/`: Contains unit tests for the application.
        *   `test_tasks.py`: Unit tests for individual task classes.
        *   `test_chatbot.py`: Unit tests for the core chatbot logic in `main.py`.
    *   `README.md`: This file, providing information about the project.
    *   `requirements.txt`: Lists the Python dependencies for the project.

## Setup and Installation

### Prerequisites

*   Python 3.7 or higher.
*   `pip` for installing packages.

### Instructions

1.  **Clone the repository** (Example command):
    ```bash
    git clone https://example.com/your-repository-name.git
    cd your-repository-name/chatbot_project 
    ```
    (Replace the URL with the actual repository URL when available.)

2.  **Create and activate a virtual environment** (Recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Application settings are managed in `chatbot_project/config/settings.py`.

Key settings include:

*   `WEATHER_API_KEY`: A placeholder for an API key for a weather service. While the current `APITask` uses the public JSONPlaceholder API (which doesn't require a key), this setting is included for future extensibility if tasks requiring API keys are added. You would replace `"YOUR_API_KEY_HERE"` with your actual key.
*   `DEFAULT_SEARCH_PATH`: The default directory used by file/text search tasks if no specific path is provided in the command. This defaults to your user's home directory (e.g., `/home/username` or `C:\Users\username`).
*   `CHATBOT_NAME`: The name of the chatbot, used in greeting and response messages.

To change these settings, simply edit the values assigned to these variables in the `settings.py` file.

## Running the Chatbot

To run the chatbot, navigate to the `chatbot_project` directory and execute:

```bash
python main.py
```

### Basic Interaction Examples:

*   **Search for a user by ID:**
    ```
    You: search_user 1
    ```
    TaskBot will fetch and display data for user ID 1 from JSONPlaceholder.

*   **Find a file in a specific directory:**
    ```
    You: find_file my_document.txt in /home/user/documents
    ```

*   **Find a file in the current directory:**
    ```
    You: find_file my_important_notes.log
    ```

*   **Search for text within files in a specific directory:**
    ```
    You: search_text 'project deadline' in /work/projects
    ```
    (Note the single quotes around the search text if it contains spaces).

*   **Exit the chatbot:**
    ```
    You: quit
    ```

## Running Tests

To ensure the reliability of the chatbot and its tasks, unit tests are provided. To run all tests, navigate to the parent directory of `chatbot_project` (if your project is `/app/chatbot_project`, `cd /app`) and run:

```bash
python -m unittest discover chatbot_project/tests
```

Alternatively, from the `chatbot_project` directory, you can run:
```bash
python -m unittest discover tests
```
Or specify individual test files:
```bash
python -m unittest tests.test_tasks
python -m unittest tests.test_chatbot
```
The tests verify the functionality of each task and the core chatbot command handling logic.

## Extending the Chatbot

TaskBot is designed to be easily extensible:

1.  **Create a New Task Class**:
    *   In the `tasks/` directory, create a new Python file for your task (e.g., `my_new_task.py`).
    *   Define a class that inherits from `tasks.base_task.Task`.
    ```python
    from .base_task import Task

    class MyNewTask(Task):
        def execute(self, query: str) -> str:
            # Your task logic here
            # Process the query and return a string result
            return f"Executed MyNewTask with query: {query}"
    ```

2.  **Implement the `execute` Method**:
    *   This method takes the user's query (as a string) and should return a string result to be displayed to the user.

3.  **Register the Task in `main.py`**:
    *   Import your new task class in `chatbot_project/main.py`:
        ```python
        from .tasks.my_new_task import MyNewTask # Adjust path as needed
        ```
    *   In the `Chatbot` class's `__init__` method, add your new task to the `self.tasks` dictionary, mapping a command keyword to your task class:
        ```python
        class Chatbot:
            def __init__(self):
                self.tasks = {
                    "search_user": APITask,
                    "find_file": SearchFileTask,
                    "search_text": SearchTextTask,
                    "my_command": MyNewTask,  # Add your new command and task
                }
        ```
    *   Update the help message in `handle_input` if necessary to include your new command.

Now, when a user types "my_command" followed by a query, your `MyNewTask` will be executed.
