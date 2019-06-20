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


## Getting started

1. Make sure you have a GitHub [personal access token](see https://github.com/settings/tokens) For full functionality, the token should have full repo, user, and notification permissions.

1. Launch BitBar and choose a plugin directory,

3. Clone this repo, and run the install script `bash install.sh` from the repo root.

4. Copy the file `GitHubMenuBar.5s.py` to the plugins directory you configured in step 2. The `.5s` naming convention tells BitBar to run this script every 5s. Feel free to modify the update frequency, keeping in mind this is only the interval at which the UI updates to match the server state, *not* how often the server does a data refresh with GitHub.

5. Ensure that the shebang in `GitHubMenuBar.5s.py` matches your system Python.

    IMPORTANT! If you're using Pyenv, you're shebang will also need to include the value of PYENV_VERSION environment variable. An example shebang would thus look like:
    `#!/usr/bin/env PYTHONIOENCODING=UTF-8 PYENV_VERSION=py-3.6.3 /path/to/pyenv/python`

6. Launch the Bitbar app! The first time the plugin runs, click the GitHub logo, then select "Click to setup GitHubMenuBar" and follow the instructions to setup your config file.

## Updating

Proper version managment is a TODO, so for now just pull the repo, and re-run the install script. Your settings are saved in your home directory and will be preserved.


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

    Each icon only appears if the count is > 0, and the GitHub icon is always present.

    Clicking on the MenuBar item activates a dropdown with with following sections:

    ![Main](screenshots/main.png?raw=true)

 - Summary: A more verbose version of the counts from the header

 - Notifications: All unread notifications

 - My Pull Requests: Summary information on your open requests, including indicators of merge conflicts, test, and review status. Each PR is color coded: red = merge conflict or test failure; orange = no failures or conflicts, but still not mergeable (usually because codeowner approval is needed); green = ready to merge.

 - Watching: Summary information on all pull requests you are involved in, either because (a) you were mentioned, or (b) your review was requested (unless you have the "MENTIONS_ONLY" setting on)

### Interactions

 - Clicking a notification or pull request links to the relevant PR on GitHub (and clears the notification)
 - Hovering over a PR shows codeowner and review information for the PR.
 - Option-clicking a PR mutes it, hiding it from the interface
 - The utilities sub-menu includes options to:
    - Access and unmute and muted PRs
    - View the PID of the GMB server process and the time of the last data refresh
    - an option to force the server to refresh data from GitHub
    - access your configuration file
    - kill the gmb server (triggering an auto-restart)


## Known issues

 - The logic for determining test status is idiosyncratic to how my company handles pull request tests. You will likely need to modify the `_get_test_status` method of [github_client.py](https://github.com/jlorince/GitHubMenuBar/blob/master/github_menubar/github_client.py) to work for your testing workflow.


 ## Planned future work

  - support for other issue mention notificiations
  - support for copying URLs from the dropdown
  - update data persistence to use SQLlite or similar
  - Add terminal-only renderer, to allow usage without BitBar
