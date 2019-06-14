# GitHubMenuBar

A MacOS menubar interface for GitHub pull requests and notifications.

## Getting started

1. Install [BitBar](https://github.com/matryer/bitbar). The setup process is simple, and will have you configure a plugins folder that we will use below.

2. Install Nerd fonts:

`brew cask install font-hack-nerd-font`

GMB relies a number of specialized glyphs that come along with these fonts. Altneratives fonts may or may not work, and are untested.

3. Clone this repository and install the package

bash
```
git clone https://github.com/jlorince/GitHubMenuBar.git
cd GitHubMenuBar
pip install .
```

4. Copy the file `GitHubMenuBar.5s.py` to the plugins directory you configured in step 1.

5. Edit `.env` as desired, and copy to yout BitBat plugins directory, or anywhere above it in the file hierarchy (e.g. your home directory). This defines some environment variables required for GMB to function.

6. (Optional): Install [teminal-notifier](https://github.com/julienXX/terminal-notifier)

    `brew install terminal-notifier`

This is required for desktop notifications for new GitHub notifications and state changes (e.g. PR test success/failure). Not required if you don't want that feature.

7. Launch the Bitbar app!

## Usage information

### Sections

 - Header. The GMB header is always available in your menubar; everything else is available in the dropdown when you click the menubar item. The header can include the following icons:

![Header](screenshots/header.png?raw=true)

These indicate, respectively:
     - The number of your unread notifications
     - The number of your open pull requests
     - The number of PRs you have with failing tests
     - The number of PRs you have with merge conflicts
     - The number of PRs you have that are mergeable

Each icon only appears if the count is > 0, and the GitHub icon is always present.




 - Summary

 - Notifications

 - My Pull Requests

 - Watching

### Interactions


## Known issues

