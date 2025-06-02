import os
from .base_task import Task

class SearchTextTask(Task):
    def execute(self, query: str) -> str:
        """
        Executes the text search task within files in a specified directory.

        The query must be in the format "'<search_text>' in <directory>".
        Note the single quotes around the search text.

        Args:
            query: The search query string.

        Returns:
            A string indicating the result of the text search. This can be:
            - A list of files and line numbers where the text was found.
            - "Search text '<search_text>' not found in '<directory>'."
            - "Error: Invalid search directory '<directory>'."
            - "Error: Invalid query format. Use ''<search_text>'' in <directory>'."
            - A summary of files that could not be read.
        """
        if not query or query.count("'") < 2 or " in " not in query:
            return "Error: Invalid query format. Use ''<search_text>'' in <directory>'."

        try:
            parts = query.split("' in ", 1)
            search_text_with_quotes = parts[0]
            
            if not search_text_with_quotes.startswith("'"):
                first_quote_index = query.find("'")
                last_quote_index = query.rfind("' in ")
                if first_quote_index == -1 or last_quote_index == -1 or first_quote_index >= last_quote_index:
                     return "Error: Invalid query format. Ensure search text is enclosed in single quotes. Use ''<search_text>'' in <directory>'."
                search_text = query[first_quote_index+1:last_quote_index]
                # The +1 for last_quote_index is to move past the space before "in"
                # The part after "in " is the directory
                # query[last_quote_index + len("' in "):]
                # Example: "'hello world' in my_folder"
                # query.split("' in ", 1) would give ["'hello world", "my_folder"]
                # Let's refine parsing for text that might contain ' in '
                
                # Find the first single quote for text start
                text_start_index = query.find("'")
                if text_start_index == -1:
                    return "Error: Invalid query format. Search text must start with a single quote. Use ''<search_text>'' in <directory>'."

                # Find the closing single quote for text end, followed by " in "
                text_end_keyword_index = query.find("' in ", text_start_index)
                if text_end_keyword_index == -1:
                    return "Error: Invalid query format. Search text must be followed by ' in <directory>'. Use ''<search_text>'' in <directory>'."

                search_text = query[text_start_index + 1 : text_end_keyword_index]
                search_directory = query[text_end_keyword_index + len("' in ") :].strip()

            else: # Original logic if the split worked as expected for simple cases
                search_text = search_text_with_quotes[1:] # Remove leading quote
                search_directory = parts[1].strip()


        except ValueError: # or specific parsing error
            return "Error: Invalid query format. Use ''<search_text>'' in <directory>'."

        if not search_text:
            return "Error: Search text cannot be empty."
        if not search_directory:
            return "Error: Directory path cannot be empty."

        if not os.path.isdir(search_directory):
            return f"Error: Invalid search directory '{search_directory}'. Path does not exist or is not a directory."

        found_occurrences = {}
        unreadable_files = []

        for root, _, files in os.walk(search_directory):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    line_numbers_found = []
                    for i, line in enumerate(lines):
                        if search_text in line:
                            line_numbers_found.append(i + 1)
                    
                    if line_numbers_found:
                        found_occurrences[file_path] = line_numbers_found
                except (IOError, UnicodeDecodeError) as e:
                    unreadable_files.append(f"{file_path} (Reason: {type(e).__name__})")
                except Exception as e: # Catch any other unexpected error during file processing
                    unreadable_files.append(f"{file_path} (Reason: Unexpected error - {type(e).__name__})")


        if not found_occurrences:
            result_message = f"Search text '{search_text}' not found in '{search_directory}'."
        else:
            result_message = f"Search text '{search_text}' found in:\n"
            for file_path, lines in found_occurrences.items():
                line_str = ", ".join(map(str, lines))
                result_message += f"- {file_path} (Lines: {line_str})\n"
        
        if unreadable_files:
            result_message += "\nCould not read the following files (or they are binary):\n"
            for f_info in unreadable_files:
                result_message += f"- {f_info}\n"
            
        return result_message.strip()

# Example Usage (for testing purposes, can be removed later)
if __name__ == '__main__':
    task = SearchTextTask()

    # Create dummy files and directories for testing
    if not os.path.exists("search_test_area"):
        os.makedirs("search_test_area/subdir")

    with open("search_test_area/file1.txt", "w") as f:
        f.write("Hello world, this is a test.\nAnother line with Hello world.\nJust a line.")
    with open("search_test_area/file2.py", "w") as f:
        f.write("# Python comment\ndef greet():\n    print('Hello world') # A greeting")
    with open("search_test_area/subdir/file3.log", "w") as f:
        f.write("Log entry 1: No target text.\nLog entry 2: Found the Hello world here.")
    with open("search_test_area/binary_file.bin", "wb") as f: # Binary file
        f.write(os.urandom(100))
    with open("search_test_area/empty.txt", "w") as f:
        pass


    print("--- Test 1: Text found in multiple files ---")
    print(task.execute("'Hello world' in search_test_area"))
    print("\n--- Test 2: Text found in a specific subdirectory file ---")
    print(task.execute("'Found the Hello world here' in search_test_area/subdir"))
    print("\n--- Test 3: Text not found ---")
    print(task.execute("'Goodbye world' in search_test_area"))
    print("\n--- Test 4: Invalid directory ---")
    print(task.execute("'Hello world' in non_existent_search_area"))
    print("\n--- Test 5: Invalid query format (missing quotes) ---")
    print(task.execute("Hello world in search_test_area"))
    print("\n--- Test 6: Invalid query format (missing 'in') ---")
    print(task.execute("'Hello world' search_test_area"))
    print("\n--- Test 7: Empty search text ---")
    print(task.execute("'' in search_test_area"))
    print("\n--- Test 8: Empty directory ---")
    print(task.execute("'Hello world' in "))
    print("\n--- Test 9: Search text containing ' in ' keyword itself ---")
    print(task.execute("'text with '' in '' keyword' in search_test_area")) # Create this file for test
    with open("search_test_area/file_with_in_keyword.txt", "w") as f:
        f.write("This is a text with '' in '' keyword indeed.")
    print(task.execute("'text with '' in '' keyword' in search_test_area"))


    # Cleanup
    os.remove("search_test_area/file1.txt")
    os.remove("search_test_area/file2.py")
    os.remove("search_test_area/subdir/file3.log")
    os.remove("search_test_area/binary_file.bin")
    os.remove("search_test_area/empty.txt")
    if os.path.exists("search_test_area/file_with_in_keyword.txt"):
        os.remove("search_test_area/file_with_in_keyword.txt")
    os.rmdir("search_test_area/subdir")
    os.rmdir("search_test_area")
