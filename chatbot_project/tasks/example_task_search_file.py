import os
from .base_task import Task

class SearchFileTask(Task):
    def execute(self, query: str) -> str:
        """
        Executes the file search task.

        The query should be in the format "<filename>" or "<filename> in <directory>".
        If no directory is provided, it searches in the current working directory.

        Args:
            query: The search query string.

        Returns:
            A string indicating the result of the file search. This can be:
            - "File found: <full_path_to_file>" if one file is found.
            - "Files found:\n<path1>\n<path2>..." if multiple files are found.
            - "File '<filename>' not found in '<directory>'." if the file is not found.
            - "Error: Invalid search directory '<directory>'." if the specified directory is invalid.
            - "Error: Invalid query format. Use '<filename>' or '<filename> in <directory>'." for malformed queries.
        """
        parts = query.lower().split(" in ", 1)
        filename_to_search = parts[0].strip()
        
        if not filename_to_search:
            return "Error: Invalid query format. Filename cannot be empty. Use '<filename>' or '<filename> in <directory>'."

        search_directory = ""
        if len(parts) > 1:
            search_directory = parts[1].strip()
        
        if not search_directory:
            search_directory = os.getcwd()

        if not os.path.isdir(search_directory):
            return f"Error: Invalid search directory '{search_directory}'. Path does not exist or is not a directory."

        found_files = []
        for root, _, files in os.walk(search_directory):
            for file in files:
                if file.lower() == filename_to_search:
                    found_files.append(os.path.join(root, file))

        if not found_files:
            return f"File '{filename_to_search}' not found in '{search_directory}'."
        elif len(found_files) == 1:
            return f"File found: {found_files[0]}"
        else:
            return "Files found:\n" + "\n".join(found_files)

# Example Usage (for testing purposes, can be removed later)
if __name__ == '__main__':
    task = SearchFileTask()
    # Create dummy files for testing
    if not os.path.exists("test_dir"):
        os.makedirs("test_dir/subdir")
    with open("test_file.txt", "w") as f:
        f.write("This is a test file.")
    with open("test_dir/test_file.txt", "w") as f:
        f.write("This is another test file in a directory.")
    with open("test_dir/subdir/another_test.log", "w") as f:
        f.write("Log file.")

    print(f"Searching for 'test_file.txt': {task.execute('test_file.txt')}")
    print(f"Searching for 'test_file.txt' in 'test_dir': {task.execute('test_file.txt in test_dir')}")
    print(f"Searching for 'another_test.log': {task.execute('another_test.log')}") # Will search CWD
    print(f"Searching for 'another_test.log' in 'test_dir/subdir': {task.execute('another_test.log in test_dir/subdir')}")
    print(f"Searching for 'non_existent_file.txt': {task.execute('non_existent_file.txt')}")
    print(f"Searching for 'test_file.txt' in 'non_existent_dir': {task.execute('test_file.txt in non_existent_dir')}")
    print(f"Searching for '' in 'test_dir': {task.execute(' in test_dir')}")


    # Cleanup dummy files and directory
    os.remove("test_file.txt")
    os.remove("test_dir/test_file.txt")
    os.remove("test_dir/subdir/another_test.log")
    os.rmdir("test_dir/subdir")
    os.rmdir("test_dir")
