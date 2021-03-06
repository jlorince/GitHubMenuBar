#!/bin/bash
osascript -e 'quit app "BitBar"'
PID_FILE=/tmp/github_menubar.pid
if test -f $PID_FILE; then
    kill $(cat $PID_FILE)
fi
launchctl unload ~/Library/LaunchAgents/com.githubmenubar.daemon.plist
rm -rf ~/.github_menubar
mkdir ~/.github_menubar

brew cask install bitbar
brew tap homebrew/cask-fonts
brew cask install font-hack-nerd-font
brew install terminal-notifier

pip install --upgrade .
python -c "from github_menubar.utils import upgrade_config, configure_plist; upgrade_config(); configure_plist()"

shebang="#!/usr/bin/env PYTHONIOENCODING=UTF-8 "
if [ -n "$PYENV_VERSION" ]; then
    shebang="$shebang PYENV_VERSION=$PYENV_VERSION "
fi
shebang=$shebang$(which python)

echo $shebang > GitHubMenuBar.5s.py
cat base_plugin_script.py >> GitHubMenuBar.5s.py
chmod +x GitHubMenuBar.5s.py

plugin_dir="$(defaults read ~/Library/Preferences/com.matryer.BitBar.plist pluginsDirectory)"
if [ -n "$plugin_dir" ]; then
    mv "$plugin_dir/GitHubMenuBar.5s.py" ./GitHubMenuBar.5s.py.bak
    cp GitHubMenuBar.5s.py "$plugin_dir/"
fi
osascript -e 'activate app "BitBar"'



