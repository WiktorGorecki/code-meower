import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

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

def configure_pre_commit():
    pre_commit_script = """
#!/bin/bash

# Ensure code-meower is installed
command -v code-meower >/dev/null 2>&1 || { echo >&2 "code-meower not found. Please install it first using 'pip install .'; exit 1; }

# Run code-meower before committing
code-meower
"""

    pre_commit_path = os.path.join('.git', 'hooks', 'pre-commit')

    if os.path.exists(pre_commit_path):
        # Update the content between #meow and #woem
        with open(pre_commit_path, 'r') as pre_commit_file:
            content = pre_commit_file.read()
            content = re.sub(r'#meow([\s\S]*?)#woem', pre_commit_script, content)

        with open(pre_commit_path, 'w') as pre_commit_file:
            pre_commit_file.write(content)
    else:
        # Create the pre-commit hook script
        with open(pre_commit_path, 'w') as pre_commit_file:
            pre_commit_file.write(pre_commit_script)

        # Make the script executable
        os.chmod(pre_commit_path, 0o755)

def update_code_meower():
    subprocess.run(['pip', 'install', '--upgrade', 'git+https://github.com/WiktorGorecki/code-meower.git'])

def uninstall_code_meower():
    subprocess.run(['pip', 'uninstall', '-y', 'code-meower'])

def main():
    parser = argparse.ArgumentParser(description='Meow - A code-meower tool')
    parser.add_argument('action', nargs='?', choices=['init', 'update', 'spit_out_the_fluff'], default='path', help='Action to perform')
    parser.add_argument('path', nargs='?', default='.', help='Path to run the censor script')

    args = parser.parse_args()

    if args.action == 'init':
        configure_pre_commit()
    elif args.action == 'update':
        update_code_meower()
    elif args.action == 'spit_out_the_fluff':
        uninstall_code_meower()
    else:
        code_directory = args.path
        custom_text = None  # Add custom text if needed

        for root, dirs, files in os.walk(code_directory):
            for file_name in files:
                if file_name.endswith('.py'):
                    file_path = os.path.join(root, file_name)

                    if check_for_dupa(file_path):
                        replace_dupa(file_path, 'replace', custom_text)
                        git_commit(file_path)

if __name__ == "__main__":
    main()
