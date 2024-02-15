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

def main():
    parser = argparse.ArgumentParser(description='Meow - A code-meower tool')
    parser.add_argument('action', choices=['init', 'update', 'spit_out_the_fluff', 'catch', 'config'], help='Action to perform')
    parser.add_argument('--path', help='Path to run the censor script', default='.')
    parser.add_argument('--word', help='Word to be substituted', default='dupa')
    parser.add_argument('--remove', help='Mark the word to be removed')
    parser.add_argument('--substitute', help='The word that the bad word will be substituted with', default='meow')

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

def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        yaml.dump(config, file)

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

def catch_censor(path='.', config=None):
    config = config or load_config()
    for root, dirs, files in os.walk(path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_name.endswith(('.py', '.yaml', '.json')):  # Add supported file formats
                process_config(file_path, config)

if __name__ == "__main__":
    main()
