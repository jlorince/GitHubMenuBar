#!/usr/bin/env bash
osascript -e 'quit app "BitBar"'
PID_FILE=/tmp/github_menubar.pid
if test -f $PID_FILE; then
    kill $(cat $PID_FILE)
fi
rm ~/.github_menubar.state.json

brew cask install bitbar
brew tap homebrew/cask-fonts
brew cask install font-hack-nerd-font
pip install --upgrade .
brew install terminal-notifier
