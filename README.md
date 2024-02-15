# Code-meower
A tool that removes all the bad words from your code before commiting it to github.

# Installation
## Release (recommended)
TODO

## Compiling
1. Download and unzip the source code
2. Run install.bat if your machine is running Windows or install.sh for Linux

# Usage:
## Configuration
You can save your global meow configuration with `meow config`

To remove a word:
```
meow config --word "abc" --remove
```
To substitute a word:
```
meow config --word "cba" --substitute ":)"
```

You can use `meow show-config` to show your configuration

## Removing words
After configuring your personal cat you have to instruct it to `catch` all the mices in your code
```
meow catch
```
