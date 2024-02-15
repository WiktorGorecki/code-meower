import os
import re
import subprocess
import json
import sys

CONFIG_FILE = os.path.expanduser('~/.meow_config.json')  # Place the config file in the user's home directory

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {}

def replace_dupa(file_path, action, custom_text=None):
    with open(file_path, 'r') as file:
        content = file.read()

    if action == 'remove':
        updated_content = re.sub(r'\bdupa\b', '', content)
    elif action == 'replace':
        updated_content = re.sub(r'\bdupa\b', 'meow', content)
    elif action == 'custom' and custom_text:
        updated_content = re.sub(r'\bdupa\b', custom_text, content)
    else:
        return  # No action specified

    with open(file_path, 'w') as file:
        file.write(updated_content)

def check_for_dupa(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    return re.search(r'\bdupa\b', content)

def git_commit(file_path):
    subprocess.run(['git', 'add', file_path])
    subprocess.run(['git', 'commit', '-m', 'Remove or replace "dupa"'])
# Don't run in code-meower's directory!!!!

def main():
    config = load_config()
    code_directory = os.getcwd()  # Use the current working directory
    action = config.get('default_action', 'remove')
    custom_text = config.get('custom_text')

    for root, dirs, files in os.walk(code_directory):
        for file_name in files:
            if file_name.endswith('.py'):
                file_path = os.path.join(root, file_name)

                if check_for_dupa(file_path):
                    replace_dupa(file_path, action, custom_text)
                    git_commit(file_path)

if __name__ == "__main__":
    main()
