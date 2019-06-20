import os

CONFIG = {
    "user": os.environ.get("GMB_USER"),
    "token": os.environ.get("GMB_TOKEN"),
    "desktop_notifications": os.environ.get("GMB_DESKTOP_NOTIFICATIONS", True)
    if os.path.exists("/usr/local/bin/terminal-notifier")
    else False,
    "port": int(os.environ.get("GMB_PORT", 9999)),
    "update_interval": int(os.environ.get("GMB_UPDATE_INTERVAL", 120)),
    "font": os.environ.get(
        "GMB_FONT", "font='Hack Regular Nerd Font Complete' size=13"
    ),
    "font_large": os.environ.get(
        "GMB_FONT_LARGE", "font='Hack Regular Nerd Font Complete' size=14"
    ),
    "mentions_only": os.environ.get("GMB_MENTIONS_ONLY", False),
    "state_path": os.environ.get(
        "GMB_STATE_PATH", f"{os.path.expanduser('~')}/.github_menubar.state.json"
    ),
    "pid_file": os.environ.get("GMB_PID_FILE", "/tmp/github_menubar.pid"),
    "collapsed": True if os.environ.get("GMB_COLLAPSED") == "true" else False,
    "config_file_path": f"{os.path.expanduser('~')}/.github_menubar.config.json",
    "log_file": "/tmp/github_menubar.log",
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

HELP_MESSAGE = """
READ THIS MESSAGE BEFORE YOU DO ANYTHING ELSE

This is the configuration file for GitHubMenubar. At a minimum you must set the values for "user"
(your GitHub username) and "token" (a GitHub personal access token, see https://github.com/settings/tokens).
For full functionality, the token should have full repo, user, and notification permissions.

Most of the other config options can be left as they are; commonly changed options are accessible through
the GitHubMenuBar utilities menu, as is this file. By default this file will be saved to $HOME/.github_menubar.config.json.

Config variable details:

    "user": Your GitHub username
    "token": Your GitHub personal access token, see https://github.com/settings/tokens).
        For full functionality, the token should have full repo, user, and notification permissions.
    "desktop_notifications": Enable or disable desktop notifications using terminal-notifier
    "port": Port on which to run the GMB server
    "update_interval": Update interval in seconds for updating the gmb server state. Making this shorter than
        the default is dangerous, as it could result in your GitHub account being rate-limited
    "font" and "font_large": Font specifications used by BitBar; Alternative fonts may or may not work, and are untested.
        Changing these variables is NOT recommended.
    "mentions_only": If true, you will only be notified for explicit mentions (not review requests). This can be
        toggled in the UI, so there should be no reason to adjust the setting here.
    "state_path": Path to file where the GMB server will persist state
    "pid_file": Path for the gmb server PID file
    "collapsed": If True, only show the GitHub logo in the menubar, without additional information. Useful if you
        don't have much space in your MenuBar
    "config_file_path": Path where this file is saved
    "log_file": Path to server log file

##### DO NOT DELETE OR MODIFY THIS LINE #####

"""
