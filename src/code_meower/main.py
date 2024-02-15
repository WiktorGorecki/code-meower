import argparse
import json
import os
import re
import sys
import yaml
from pathlib import Path

CONFIG_FILE = os.path.expanduser('~/.meow_config.yaml')  # Place the config file in the user's home directory

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return yaml.safe_load(file)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        yaml.dump(config, file)

def process_config(file_path, config):
    with open(file_path, 'r') as file:
        content = file.read()

    for file_format, words in config.items():
        if file_path.endswith(file_format):
            for word, actions in words.items():
                for action, action_params in actions.items():
                    if action == 'substitute':
                        substitute = action_params.get('substitute', 'meow')
                        content = re.sub(rf'\b{word}\b', substitute, content)
                    elif action == 'remove':
                        content = re.sub(rf'\b{word}\b', '', content)

    with open(file_path, 'w') as file:
        file.write(content)

def edit_config(word, remove, substitute):
    config = load_config()

    if word not in config:
        config[word] = {}

    if remove:
        config[word]['remove'] = True
        config[word].pop('substitute', None)
    elif substitute:
        config[word]['substitute'] = substitute
        config[word].pop('remove', None)

    save_config(config)

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

def catch_censor(path='.', config=None):
    config = config or load_config()
    for root, dirs, files in os.walk(path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_name.endswith(('.py', '.yaml', '.json')):  # Add supported file formats
                process_config(file_path, config)

def main():
    parser = argparse.ArgumentParser(description='Meow - A code-meower tool')
    parser.add_argument('action', choices=['init', 'update', 'spit_out_the_fluff', 'catch', 'config'],
                        help='Action to perform')
    parser.add_argument('--path', help='Path to run the censor script', default='.')
    parser.add_argument('--word', help='Word to configure')
    parser.add_argument('--remove', action='store_true', help='Remove the specified word')
    parser.add_argument('--substitute', help='Substitute for the specified word')

    args = parser.parse_args()

    if args.action == 'init':
        configure_pre_commit()
    elif args.action == 'update':
        update_code_meower()
    elif args.action == 'spit_out_the_fluff':
        print("Uninstalling code-meower...")
    elif args.action == 'catch':
        config = load_config()
        catch_censor(args.path, config)
    elif args.action == 'config':
        if not args.word or (not args.remove and not args.substitute):
            print("Please provide --word and either --remove or --substitute.")
            sys.exit(1)
        edit_config(args.word, args.remove, args.substitute)

if __name__ == "__main__":
    main()
