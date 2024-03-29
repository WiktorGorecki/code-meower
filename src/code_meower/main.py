import argparse
import json
import os
import re
import subprocess
import sys
import yaml

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
    print(f"Processing config for file: {file_path}")

    with open(file_path, 'r', newline='') as file:
        content = file.read()

    for word, actions in config.items():
        if isinstance(actions, str):  # Check if actions is a string
            replacement = actions
            content = re.sub(rf'\b{re.escape(word.strip())}\b', replacement, content)
            # print(f"Found word: {word.strip()}, substituted with: {replacement}")
        elif isinstance(actions, dict):  # Check if actions is a dictionary
            replacement = actions.get('substitute', 'meow')
            content = re.sub(rf'\b{re.escape(word.strip())}\b', replacement, content)
            # print(f"Found word: {word.strip()}, substituted with: {replacement}")
        elif 'remove' in actions:
            content = re.sub(rf'\b{re.escape(word.strip())}\b', '', content)
            print(f"Found word: {word.strip()}, removed")

    with open(file_path, 'w', newline='', encoding='utf-8', errors='ignore') as file:
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
command -v meow >/dev/null 2>&1 || { echo >&2 "code-meower not found. Please install it first using 'pip install .'"; exit 1; }

# Run code-meower before committing
meow
"""

    git_hooks_dir = os.path.join('.git', 'hooks')
    pre_commit_path = os.path.join(git_hooks_dir, 'pre-commit')

    if os.path.exists(pre_commit_path):
        # Update the content between #meow and #woem
        with open(pre_commit_path, 'r') as pre_commit_file:
            content = pre_commit_file.read()
            content = re.sub(r'#meow([\s\S]*?)#woem', pre_commit_script, content)

        with open(pre_commit_path, 'w') as pre_commit_file:
            pre_commit_file.write(content)
    else:
        # Create the .git/hooks directory if it doesn't exist
        os.makedirs(git_hooks_dir, exist_ok=True)

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
    # print(f"Searching for files to censor in: {path}")
    config = config or load_config()
    for root, dirs, files in os.walk(path):
        if '.git' in dirs:
            dirs.remove('.git')
        for file_name in files:
            file_path = os.path.join(root, file_name)
            # print(f"Found file: {file_path}")
            process_config(file_path, config)

def show_config():
    config = load_config()
    print(json.dumps(config, indent=2))

def main():
    parser = argparse.ArgumentParser(description='Meow - A code-meower tool')
    subparsers = parser.add_subparsers(dest='action', metavar='action', help='Action to perform')

    catch_parser = subparsers.add_parser('catch', help='Catch and censor text files')
    catch_parser.add_argument('--path', help='Path to run the censor script', default='.')

    config_parser = subparsers.add_parser('config', help='Edit configuration')
    config_parser.add_argument('--word', help='Word to configure')
    config_parser.add_argument('--remove', action='store_true', help='Remove the specified word')
    config_parser.add_argument('--substitute', help='Substitute for the specified word')

    subparsers.add_parser('init', help='Configure pre-commit hook')
    subparsers.add_parser('update', help='Update code-meower')
    subparsers.add_parser('spit_out_the_fluff', help='Uninstall code-meower').set_defaults(func=uninstall_code_meower)
    subparsers.add_parser('show-config', help='Show current configuration').set_defaults(func=show_config)

    args = parser.parse_args()

    if args.action == 'init':
        configure_pre_commit()
    elif args.action == 'update':
        update_code_meower()
    elif args.action == 'spit_out_the_fluff':
        print("Uninstalling code-meower...")
        uninstall_code_meower()
    elif args.action == 'catch':
        config = load_config()
        catch_censor(args.path, config)
    elif args.action == 'config':
        if not args.word or (not args.remove and not args.substitute):
            print("Please provide --word and either --remove or --substitute.")
            sys.exit(1)
        edit_config(args.word, args.remove, args.substitute)
    elif args.action == 'show-config':
        show_config()
    elif hasattr(args, 'func'):
        args.func()
    elif args.action:
        print("Invalid arguments")
        sys.exit(1)

if __name__ == "__main__":
    main()
