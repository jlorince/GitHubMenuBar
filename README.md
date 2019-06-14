# GitHubMenuBar

A MacOS menubar interface for GitHub pull requests and notifications.

This code is a work-in-progress, but is entirely read-only. You may have some issues, but shouldn't have to worry about anything breaking with your repositories. Pull requests and issue reports are welcome and encouraged.

## Requirements

 - Python 3.6+
 - MacOS 10.7+
 - [BitBar](https://github.com/matryer/bitbar)
 - [Nerd fonts](https://github.com/ryanoasis/nerd-fonts)
 - [teminal-notifier](https://github.com/julienXX/terminal-notifier) (Optional)


## Getting started

1. Install [BitBar](https://github.com/matryer/bitbar). The setup process is simple, and will have you configure a plugins folder that we will use below.

2. Install Nerd fonts:

    ```
    brew tap homebrew/cask-fonts
    brew cask install font-hack-nerd-font
    ```

    GMB relies a number of specialized glyphs that come along with these fonts. Altneratives fonts may or may not work, and are untested.

3. Clone this repository and install the package


    ```
    git clone https://github.com/jlorince/GitHubMenuBar.git
    cd GitHubMenuBar
    pip install .
   ```

4. Copy the file `GitHubMenuBar.5s.py` to the plugins directory you configured in step 1. The `.5s` naming convention tells BitBar to run this script every 5s. Feel free to modify the update frequency, keeping in mind this is only the interval at which the UI updates to match the server state, *not* how often the server does a data refresh with GitHub.

5. Edit `.env` as desired, and copy to your BitBar plugins directory, or anywhere above it in the file hierarchy (e.g. your home directory). This defines some environment variables required for GMB to function. At a minimum you will need to set your GitHub username and access token in this file, though other options can be configured.

6. (Optional): Install [teminal-notifier](https://github.com/julienXX/terminal-notifier)

    `brew install terminal-notifier`

    This is required for desktop notifications for new GitHub notifications and state changes (e.g. PR test success/failure). Not required if you don't want that feature.

7. Ensure that the shebang in `GitHubMenuBar.5s.py` matches your system Python (or whatever python you did the `pip install` for)

8. Launch the Bitbar app!

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


## Known issues

 - The logic for determining test status is idiosyncratic to how my company handles pull request tests. You will likely need to modify the `_get_test_status` method of [github_client.py](https://github.com/jlorince/GitHubMenuBar/blob/master/github_menubar/github_client.py) to work for your testing workflow.


 ## Planned future work

  - support for other issue mention notificiations
  - support for copying URLs from the dropdown
  - update data persistence to use SQLlite or similar
  - Add terminal-only renderer, to allow usage without BitBar
