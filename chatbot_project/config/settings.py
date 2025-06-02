"""
Configuration settings for the chatbot application.
"""

import os

# API Key for a hypothetical weather service
# Replace "YOUR_API_KEY_HERE" with your actual API key if you integrate such a service.
WEATHER_API_KEY = "YOUR_API_KEY_HERE"

# Default search path for file and text search tasks
# This defaults to the user's home directory (e.g., /home/username or C:\\Users\\username)
DEFAULT_SEARCH_PATH = os.path.expanduser("~")

# General application settings
CHATBOT_NAME = "TaskBot"
LOG_LEVEL = "INFO"  # For future logging integration (e.g., DEBUG, INFO, WARNING, ERROR)

# You can add other settings here as the application grows, for example:
# MAX_SEARCH_RESULTS = 10
# REQUEST_TIMEOUT = 30  # seconds for API requests
# DEFAULT_LANGUAGE = "en"
