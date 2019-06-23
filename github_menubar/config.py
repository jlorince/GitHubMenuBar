import os

CONFIG = {
    "font": "font='Hack Regular Nerd Font Complete' size=13",
    "font_large": "font='Hack Regular Nerd Font Complete' size=14",
    "pid_file": "/tmp/github_menubar.pid",
    "config_file_path": f"{os.path.expanduser('~')}/.github_menubar.config.yaml",
    "log_file": "/tmp/github_menubar.log",
    "state_path": f"{os.path.expanduser('~')}/.github_menubar.state.json"
}

# https://www.reddit.com/r/asciiart/comments/ai0787/fuck_yeah_im_a_trex/
TREX = ".................................. ....................................._,-~\"¯¯\"~-,\n.................................................. ................__„-~\"¯¯:::,-~~-,_::::\"-\n.................................................. ..........„~\"¯::::::::::::::\"::::::::::::::::::::::\\\n.................................................. .__„„„-\"::::::::::::::::::::::::::::::::::::::::::::::\"~-,\n..........................................__-~\"::,-':::::::::::::::::::::::::::::::::::::::::::::::::::::::: ::::~-,\n..........................._______~\"___-~\"::::::::::::::::::::::::::::::::::::::::::::: ::: :: :::::::::::\"-,\n......................,~\"::::::::::::::¯¯::::::::: ::::::::::::::::::::::::: :::::::::::::::::::::::::::::::::::::::::,: │\n....................:/:::::::::::::::::__-~\":::::::::::::::::::::::::::::::::::::::::::::::::_,-~\":'\\'-,:\\:│:\\│::\\│\\::\\:│\n...................,'::::::::,-~~\"~\"_::',::│::::::::::::::::::::::::::::::::::: :: :::,~ ':\\'-,::',\"-\\::'':\"::::::::\\│:│/\n..............._,-'\"~----\":::/,~\"¯\"-:│::│::│:::::::::::::::::::::::::::::::::::,~\"::\\'-,:\\;;'-';;;;;;;;;;;,-'::\\::│/\n............,-'::::::::::::::::'-\\~\"O¯_/::,'::│:::::::::::::::::::::::::::::::::,-',::\\'-,:│::\";;;;;;;;;;;;,-':\\:'-,::\\\n............│:::::::::::::::::-,_'~'::::,-'::,':::::::::::::::::::::::::::::,-':\\'-,:\\'-,';;';;;;;;;;;;;;;,-':\\:::'\\-,│''\n............│::,-~\"::::::::::::::\"~~\":::,-'::::::::::::::::::::::::_,-~':\\'-,│:\"'\";;;;;;;;;;;;;;,-'¯::'-,:',\\│\n.........../::/::::::::::::::::::::::::::::::::::::::::::::_,„-~\"¯\\:\\'-,│;''-';;;;;;;;;;;;;;;;;;,-'--,::\\-:\\:\\│\n........./::::│:::::::::::::::::::::::::::::::::::::::::,-';;'-';;;;',/;\\/;;;;;;;;;;;;;;;;;;;;,-,│:::\\-,:│\\│..\\│\n......./:::::::\\:::::::::::::::::::::::::::::::::::::,-';;;;;;;;;;;;;;;;;;;;;;;;;;;,-~'''(\"-,\\:::│\\:│::''\n......,':::::::,'::::::::::::::::::::::::::::::::: :,-'/;;;;;;;;;;;;;;;;;;;;;;;;;,--'::::::/\"~'\n.....,'::::::::│:::::::::::::::::::::::::::::,„-~\"::│;;;;;;;;;;;;;;;;;;;;;,-'::::::::,'::::/\n..../:::::::::│:::::::::::::„---~~\"\"¯¯¯::',:::::,';;;;;;;;;;;;;;;;;;;,'::::::::: :: │_,-'\n..,'::::::::::::\",:,-~\"¯::::::::\"-,::::::::::│:::/;;;;;;;;;;;;;;;;;;;,':::::::│::::,'\n./:::::::::::::::│:::::::::::::::::::\"-,:::::::\\:::│¯¯¯\"\"\"~-,~,_/::::::::,':::/\n::::::::::::::::::::::::::::::::::::::\"~-,_::│::\\: : : : : : │: : \\::::::::/:/\n::::::::::::::::::::::::::::::\",:::::::::::::\"-':::\\: : : : : : │: : :\\::::::\\ FUCK YEAH I'M A T-REX\n::::::::::::::::::::::::::::::::\",:::::::::::::: ::::\\: : : : : : \\: : : │:::::;;\\\n::::::::::::::::::\"-,:::::::::::::::\",:::::::::::::::/│\\ ,: : : : : : : │::::,'/│::::│\n:::::::::::::::::::::\"-,:::::::::::::::\"-,_::::::::::\\│:/│,: : : : : : : │::: │'-,/│:::│\n::::::::::::::::::::::::\"~-,_::::::::::::::\"~-,_:::\"-,/│/\\::::::::::: \\::: \\\"-/│::│\n:::::::::::::::::::::::::::::::\"~-,__:::::::::::',\"-,:::\"_│/\\:│\\: : : : \\::\\\":/│\\│\n::::::::::::::::::::::::::::::::::::::::\"~-,_:::::\\:::\\:::\"~/_:│:│\\: : : '-,\\::\"::,'\\\n:::::::::::::::::::::::::::::::::::::::::::::::\"-,_:'-,::\\:::::::\"-,│:│\\,-, : '-,\\:::│-'-„\n:::::::::::::::::::::::::::::::::::::::::::::::::: ::,-,'\"-:\"~,:::::\"/_/::│-/\\--';;\\:::/: │\\-,\n:::::::::::::::::::::::::::::::::::::::::::::::::: :/...'-,::::::\"~„::::\"-,/_:│:/\\:/│/│/│_/:│\n:::::::::::::::::::::::::::::::::::::::::::::::::: │......\"-,::::::::\"~-:::::\"\"~~~\"¯:::│\n:::::::::::::::::::::::::::::::::::::::::::::::::: │.........\"-,_::::::::::::::::::::::::::::/\n:::::::::::::::::::::::::::::::::::::::::::::::::\\ ..............\"~--„_____„„-~~\"\n Also, there's nothing to show right now"

COLORS = {"red": "#cc1c26", "orange": "#fc9936", "green": "green"}

GLYPHS = {
    "merged_pr": "\uf419",  # 
    "open_pr": "\uf407",  # 
    "closed_pr": "\uf659",  # 
    "tests": "\uf188",  # 
    "null": "\ufce0",  # ﳠ
    "github_logo": "\uf408",  # 
    "bell": "\uf599",  # 
    "x": "\uf00d",  # 
    "in_progress": "\uf10c",  # 
    "success": "\uf058",  # 
    "error": "\uf06a",  # 
    "na": "\uf6d7",  # 
    "comment": "\uf679",  # 
    "approval": "\uf67e",  # 
    "cancelled": "\ufc38",  # ﰸ
    "change_request": "\uf67c",  # 
}

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

# CHANGING ANY SETTING BELOW THIS LINE IS NOT RECOMMENDED

#  Update interval in seconds for updating the gmb server state. Making this shorter than
# the default is dangerous, as it could result in your GitHub account being rate-limited
update_interval: 120
#  Font specifications used by BitBar; Alternative fonts may or may not work, and are untested.
font: "font='Hack Regular Nerd Font Complete' size=13"
font_large: "font='Hack Regular Nerd Font Complete' size=14"
"""
