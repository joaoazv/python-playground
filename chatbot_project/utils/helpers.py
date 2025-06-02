"""
Helper functions for the chatbot application.
"""

import requests
from typing import Optional, Any

def make_api_request(
    url: str, 
    params: Optional[dict] = None, 
    headers: Optional[dict] = None
) -> Optional[Any]:
    """
    Makes a GET request to the specified URL and returns the JSON response.

    Args:
        url: The URL to make the request to.
        params: Optional dictionary of URL parameters.
        headers: Optional dictionary of request headers.

    Returns:
        A dictionary or list representing the parsed JSON response if the
        request is successful (status code 200), otherwise None.
    """
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10) # Added timeout
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)

        # Check for successful status code, though raise_for_status covers most non-200s
        if response.status_code == 200:
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError as json_err:
                print(f"Error: Failed to decode JSON response from {url}. Error: {json_err}")
                return None
        else:
            # This block might be less likely to be hit due to raise_for_status,
            # but kept for explicitness or if raise_for_status is removed.
            print(f"Error: API request to {url} failed with status code {response.status_code}. Response: {response.text}")
            return None

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while requesting {url}: {http_err} (Status code: {http_err.response.status_code})")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred while requesting {url}: {conn_err}")
        return None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred while requesting {url}: {timeout_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected error occurred while requesting {url}: {req_err}")
        return None

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    print("--- Testing make_api_request ---")

    # Test with JSONPlaceholder (valid request)
    user_data = make_api_request("https://jsonplaceholder.typicode.com/users/1")
    if user_data:
        print(f"Successfully fetched user 1: Name - {user_data.get('name')}")
    else:
        print("Failed to fetch user 1.")

    # Test with a non-existent user (should be a 404)
    non_existent_user = make_api_request("https://jsonplaceholder.typicode.com/users/99999")
    if non_existent_user:
        print(f"Fetched non-existent user (unexpected): {non_existent_user}")
    else:
        print("Correctly failed to fetch non-existent user (e.g., 404).")
        
    # Test with a non-JSON response URL (if you have one, or expect failure)
    # For example, a URL that returns HTML
    html_response = make_api_request("https://example.com")
    if html_response:
        print(f"Fetched HTML from example.com (unexpectedly parsed as JSON): {html_response}")
    else:
        print("Correctly failed to parse HTML from example.com as JSON.")

    # Test with an invalid URL
    invalid_url_response = make_api_request("https://thisurldoesnotexist.invalidtld")
    if invalid_url_response:
        print("Fetched from invalid URL (unexpected).")
    else:
        print("Correctly failed to fetch from an invalid URL.")
