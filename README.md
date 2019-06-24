# GitHubMenuBar

A MacOS menubar interface for GitHub pull requests and notifications.

This code is a work-in-progress, but is entirely read-only. You may have some issues, but shouldn't have to worry about anything breaking with your repositories. Pull requests and issue reports are welcome and encouraged.

## Requirements

 - Python 3.6+
 - MacOS 10.7+
 - [HomeBrew](https://brew.sh/)
 - [BitBar](https://github.com/matryer/bitbar) (handled by install script)
 - [Nerd fonts](https://github.com/ryanoasis/nerd-fonts) (handled by install script)
 - [teminal-notifier](https://github.com/julienXX/terminal-notifier) (Optional, handled by install script)

## Updating

If you already have GMB configured and running, just pull down the repo, run the install script again, and you're all set!

## Getting started for the first time

1. Make sure you have a GitHub [personal access token](https://github.com/settings/tokens) For full functionality, the token should have full repo, user, and notification permissions.

2. Clone this repo, and run the install script (`bash install.sh`) from the repo root. BitBar will automatically launch when installation completes.

3. If you had BitBar installed prior to installation, the install script should have copied the auto-generated script to your BitBar plugins directory, so move on to step 4. If not, when the BitBar app launches it will prompt you to select your plugins directory. Do so, and copy `GitHubMenuBar.5s.py` from repo root to the plugins directory (this file will have been generated automatically by the install script).

4, At this point BitBar should be running and you'll see a GitHub icon in your MenuBar. Click it, and select the open to setup GMB. This will open a config file in your terminal.

5. Set your GitHub access token and username in the config file, and you're all set.

## How does it work?

TODO - add basic architecture overview.

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

    Each icon only appears if the count is > 0, and the GitHub icon is always present. If the app takes up too much space in your menubar, you can select "Collapse MenuBar icons" in the options menu to only show the logo at all times.

    Clicking on the MenuBar item activates a dropdown with with following sections:

    ![Main](screenshots/main.png?raw=true)

 - Summary: A more verbose version of the counts from the header

 - Notifications: All unread notifications

 - My Pull Requests: Summary information on your open requests, including indicators of merge conflicts, test, and review status. Each PR is color coded: red = merge conflict or test failure; orange = no failures or conflicts, but still not mergeable (usually because codeowner approval is needed); green = ready to merge.

 - Watching: Summary information on all pull requests you are involved in, either because (a) you were mentioned, or (b) your review was requested (unless you have the "MENTIONS_ONLY" setting on)

### Interactions

 - Clicking a notification or pull request links to the relevant PR on GitHub (and clears the notification)
 - Hovering over a PR shows codeowner and review information for the PR, and gives an option to mute it. If you mute a PR, it will be hidden from the interface and you won't receive any notifications for it (you can view and unmute muted PRs through the utilities menu).
 - Option-clicking a PR or notification copies the corresponding URL to the clipboard.
 - The utilities sub-menu includes options to:
    - access and unmute muted PRs
    - view the PID of the GMB server process and the time of the last data refresh
    - force the server to refresh data from GitHub
    - kill the gmb server (triggering an auto-restart)

## Debugging

 - The install script should automatically configure this, but if you're seeing python import issues, double-check that that the shebang in `GitHubMenuBar.5s.py` matches your system Python. If you're using Pyenv, you're shebang will also need to include the value of PYENV_VERSION environment variable. An example would thus look like:
    `#!/usr/bin/env PYTHONIOENCODING=UTF-8 PYENV_VERSION=py-3.6.3 /path/to/pyenv/python


 ## Planned future work

  - support for other issue mention notificiations
  - Done: ~support for copying URLs from the dropdown~
  - update data persistence to use SQLlite or similar
  - Add terminal-only renderer, to allow usage without BitBar (though this sorta makes the name inaccurate...)
  - Support for team mention notifications.
  - More PR metadata (test details, etc.) available in sub-menus
