#!/usr/bin/env bash
brew cask install bitbar
brew tap homebrew/cask-fonts
brew cask install font-hack-nerd-font
git clone https://github.com/jlorince/GitHubMenuBar.git
cd GitHubMenuBar
pip install .
brew install terminal-notifier
