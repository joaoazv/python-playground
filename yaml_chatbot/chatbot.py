import re
import yaml
import os
import tempfile
import zipfile
import shutil

def parse_input(text):
    """
    Parses the user input to extract application name, environments, and pod counts.
    """
    app_name_match = re.search(r'application name "([^"]+)"', text)
    if not app_name_match:
        return None

    app_name = app_name_match.group(1)

    environments = {}

    # Find all clauses like "in Env1 and Env2 with X pods"
    pattern = r'in ([\w\s,and]+?) with (\d+)\s+pods?'
    for match in re.finditer(pattern, text):
        env_names_str = match.group(1)
        pod_count = int(match.group(2))

        # Extract individual environment names from the clause
        env_names = re.findall(r'[A-Z][a-z]*', env_names_str)
        for env in env_names:
            environments[env.lower()] = pod_count

    if not environments:
        return None

    return {'app_name': app_name, 'environments': environments}

def generate_yaml_content(app_name, env, pods):
    """
    Generates the YAML content for a specific environment.
    """
    data = {
        'application': {
            'name': app_name,
            'environment': env,
            'replicaCount': pods,
        }
    }
    return yaml.dump(data, default_flow_style=False)

def create_zip_archive(app_name, configs):
    """
    Creates a zip archive containing the generated YAML files.

    Args:
        app_name (str): The name of the application.
        configs (dict): A dictionary where keys are environment names and values are YAML content.

    Returns:
        str: The name of the created zip file.
    """
    temp_dir = tempfile.mkdtemp()
    try:
        for env, yaml_content in configs.items():
            file_path = os.path.join(temp_dir, f'application-{env}.yaml')
            with open(file_path, 'w') as f:
                f.write(yaml_content)

        zip_filename_base = f'{app_name}-config'
        zip_filename = f'{zip_filename_base}.zip'

        # To avoid issues with existing files, let's create the zip in the current dir
        shutil.make_archive(zip_filename_base, 'zip', temp_dir)

        return zip_filename
    finally:
        shutil.rmtree(temp_dir)

def main():
    """
    The main function for the chatbot CLI.
    """
    print("Welcome to the YAML Chatbot!")
    print("You can ask me to generate application configurations.")
    print("For example: 'Generate an \"application-config\" for application name \"my-app\" that will be deployed in Dev with 1 pod.'")
    print("Type 'quit' or 'exit' to stop.")

    while True:
        user_input = input("\n> ")
        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break

        parsed_data = parse_input(user_input)

        if not parsed_data:
            print("I'm sorry, I couldn't understand that request. Please try again.")
            continue

        app_name = parsed_data['app_name']
        environments = parsed_data['environments']

        yaml_configs = {}
        for env, pods in environments.items():
            yaml_configs[env] = generate_yaml_content(app_name, env, pods)

        try:
            zip_filename = create_zip_archive(app_name, yaml_configs)
            print(f"Successfully created '{zip_filename}' in the current directory.")
        except Exception as e:
            print(f"An error occurred while creating the zip file: {e}")

if __name__ == "__main__":
    main()
