from typing import Optional
import requests
from .base_task import Task

class APITask(Task):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key  # Not used in this example, but good practice

    def execute(self, query: str) -> str:
        """
        Executes the API task by fetching user data from JSONPlaceholder
        using the provided user ID (query).

        Args:
            query: The user ID (e.g., "1", "2") for the JSONPlaceholder API.

        Returns:
            A string containing the user's name, email, and company name
            if found, or an error message if the user is not found, the API
            request fails, or an invalid user ID is provided.
        """
        if not query.isdigit() or int(query) <= 0:
            return "Invalid user ID provided. Please provide a positive integer."

        user_id = query
        api_url = f"https://jsonplaceholder.typicode.com/users/{user_id}"

        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)

            if response.status_code == 200:
                user_data = response.json()
                name = user_data.get("name", "N/A")
                email = user_data.get("email", "N/A")
                company_name = user_data.get("company", {}).get("name", "N/A")

                return (
                    f"User Found:\n"
                    f"  Name: {name}\n"
                    f"  Email: {email}\n"
                    f"  Company: {company_name}"
                )
            # This else block might be redundant due to raise_for_status,
            # but kept for explicit handling of other 2xx codes if any in future.
            else:
                return f"Error: Received status code {response.status_code}. User not found or API error."

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 404:
                return f"Error: User with ID '{user_id}' not found (404)."
            else:
                return f"HTTP error occurred: {http_err} (Status code: {response.status_code})"
        except requests.exceptions.RequestException as e:
            return f"Error: API request failed. {e}"
        except ValueError: # Handles JSON decoding errors if response is not valid JSON
            return "Error: Could not decode JSON response from the API."
