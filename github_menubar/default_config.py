DEFAULT_CONFIG = """
# This is the configuration file for GitHubMenubar. At a minimum you must set the values for "user"
# (your GitHub username) and "token" (a GitHub personal access token, see https://github.com/settings/tokens).
# For full functionality, the token should have full repo, user, and notification permissions.

# Most of the other config options can be left as they are; commonly changed options are accessible through
# the GitHubMenuBar utilities menu, as is this file. This file will be saved to $HOME/.github_menubar.config.yaml.

# Your GitHub username
user: null
# Your GitHub personal access token, see https://github.com/settings/tokens).
# For full functionality, the token should have full repo, user, and notification permissions.
token: null
# Enable or disable desktop notifications using terminal-notifier
desktop_notifications: true
# If true, you will only be notified for explicit mentions (not review requests).
mentions_only: false
# If True, only show the GitHub logo in the menubar, without additional information. Useful if you
# don't have much space in your MenuBar
collapsed: false
# Port on which to run the GMB server
port: 9999
# Path to file where the GMB server will persist state
state_path: "~/.github_menubar.state.json"
# Path for the gmb server PID file
pid_file: "/tmp/github_menubar.pid"
# Path to server log file
log_file: "/tmp/github_menubar.log"

# CHANGING ANY SETTING BELOW THIS LINE IS NOT RECOMMENDED

#  Update interval in seconds for updating the gmb server state. Making this shorter than
# the default is dangerous, as it could result in your GitHub account being rate-limited
update_interval: 120
#  Font specifications used by BitBar; Alternative fonts may or may not work, and are untested.
font: "font='Hack Regular Nerd Font Complete' size=13"
font_large: "font='Hack Regular Nerd Font Complete' size=14"
"""
