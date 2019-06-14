import os
from subprocess import getoutput

CONFIG = {
    "desktop_notifications": os.environ.get("GMB_DESKTOP_NOTIFICATIONS", True) if getoutput("which terminal-notifier") else False,
    "port": int(os.environ.get("GMB_PORT", 9999)),
    "token": os.environ.get("GMB_TOKEN"),
    "update_interval": int(os.environ.get("GMB_UPDATE_INTERVAL", 120)),
    "user": os.environ.get("GMB_USER"),
    "font": os.environ.get("GMB_FONT", "font='Hack Regular Nerd Font Complete' size=13"),
    "font_large": os.environ.get("GMB_FONT_LARGE", "font='Hack Regular Nerd Font Complete' size=14"),
    "mentions_only": os.environ.get("GMB_MENTIONS_ONLY", False),
    "state_path": os.environ.get("GMB_STATE_PATH", f"{os.path.expanduser('~')}/.gitmenubar.json"),
    "pid_file": os.environ.get("GMB_PID_FILE", "/tmp/github_menubar.pid")
}
# https://www.reddit.com/r/asciiart/comments/ai0787/fuck_yeah_im_a_trex/
TREX = ".................................. ....................................._,-~\"¯¯\"~-,\n.................................................. ................__„-~\"¯¯:::,-~~-,_::::\"-\n.................................................. ..........„~\"¯::::::::::::::\"::::::::::::::::::::::\\\n.................................................. .__„„„-\"::::::::::::::::::::::::::::::::::::::::::::::\"~-,\n..........................................__-~\"::,-':::::::::::::::::::::::::::::::::::::::::::::::::::::::: ::::~-,\n..........................._______~\"___-~\"::::::::::::::::::::::::::::::::::::::::::::: ::: :: :::::::::::\"-,\n......................,~\"::::::::::::::¯¯::::::::: ::::::::::::::::::::::::: :::::::::::::::::::::::::::::::::::::::::,: │\n....................:/:::::::::::::::::__-~\":::::::::::::::::::::::::::::::::::::::::::::::::_,-~\":'\\'-,:\\:│:\\│::\\│\\::\\:│\n...................,'::::::::,-~~\"~\"_::',::│::::::::::::::::::::::::::::::::::: :: :::,~ ':\\'-,::',\"-\\::'':\"::::::::\\│:│/\n..............._,-'\"~----\":::/,~\"¯\"-:│::│::│:::::::::::::::::::::::::::::::::::,~\"::\\'-,:\\;;'-';;;;;;;;;;;,-'::\\::│/\n............,-'::::::::::::::::'-\\~\"O¯_/::,'::│:::::::::::::::::::::::::::::::::,-',::\\'-,:│::\";;;;;;;;;;;;,-':\\:'-,::\\\n............│:::::::::::::::::-,_'~'::::,-'::,':::::::::::::::::::::::::::::,-':\\'-,:\\'-,';;';;;;;;;;;;;;;,-':\\:::'\\-,│''\n............│::,-~\"::::::::::::::\"~~\":::,-'::::::::::::::::::::::::_,-~':\\'-,│:\"'\";;;;;;;;;;;;;;,-'¯::'-,:',\\│\n.........../::/::::::::::::::::::::::::::::::::::::::::::::_,„-~\"¯\\:\\'-,│;''-';;;;;;;;;;;;;;;;;;,-'--,::\\-:\\:\\│\n........./::::│:::::::::::::::::::::::::::::::::::::::::,-';;'-';;;;',/;\\/;;;;;;;;;;;;;;;;;;;;,-,│:::\\-,:│\\│..\\│\n......./:::::::\\:::::::::::::::::::::::::::::::::::::,-';;;;;;;;;;;;;;;;;;;;;;;;;;;,-~'''(\"-,\\:::│\\:│::''\n......,':::::::,'::::::::::::::::::::::::::::::::: :,-'/;;;;;;;;;;;;;;;;;;;;;;;;;,--'::::::/\"~'\n.....,'::::::::│:::::::::::::::::::::::::::::,„-~\"::│;;;;;;;;;;;;;;;;;;;;;,-'::::::::,'::::/\n..../:::::::::│:::::::::::::„---~~\"\"¯¯¯::',:::::,';;;;;;;;;;;;;;;;;;;,'::::::::: :: │_,-'\n..,'::::::::::::\",:,-~\"¯::::::::\"-,::::::::::│:::/;;;;;;;;;;;;;;;;;;;,':::::::│::::,'\n./:::::::::::::::│:::::::::::::::::::\"-,:::::::\\:::│¯¯¯\"\"\"~-,~,_/::::::::,':::/\n::::::::::::::::::::::::::::::::::::::\"~-,_::│::\\: : : : : : │: : \\::::::::/:/\n::::::::::::::::::::::::::::::\",:::::::::::::\"-':::\\: : : : : : │: : :\\::::::\\ FUCK YEAH I'M A T-REX\n::::::::::::::::::::::::::::::::\",:::::::::::::: ::::\\: : : : : : \\: : : │:::::;;\\\n::::::::::::::::::\"-,:::::::::::::::\",:::::::::::::::/│\\ ,: : : : : : : │::::,'/│::::│\n:::::::::::::::::::::\"-,:::::::::::::::\"-,_::::::::::\\│:/│,: : : : : : : │::: │'-,/│:::│\n::::::::::::::::::::::::\"~-,_::::::::::::::\"~-,_:::\"-,/│/\\::::::::::: \\::: \\\"-/│::│\n:::::::::::::::::::::::::::::::\"~-,__:::::::::::',\"-,:::\"_│/\\:│\\: : : : \\::\\\":/│\\│\n::::::::::::::::::::::::::::::::::::::::\"~-,_:::::\\:::\\:::\"~/_:│:│\\: : : '-,\\::\"::,'\\\n:::::::::::::::::::::::::::::::::::::::::::::::\"-,_:'-,::\\:::::::\"-,│:│\\,-, : '-,\\:::│-'-„\n:::::::::::::::::::::::::::::::::::::::::::::::::: ::,-,'\"-:\"~,:::::\"/_/::│-/\\--';;\\:::/: │\\-,\n:::::::::::::::::::::::::::::::::::::::::::::::::: :/...'-,::::::\"~„::::\"-,/_:│:/\\:/│/│/│_/:│\n:::::::::::::::::::::::::::::::::::::::::::::::::: │......\"-,::::::::\"~-:::::\"\"~~~\"¯:::│\n:::::::::::::::::::::::::::::::::::::::::::::::::: │.........\"-,_::::::::::::::::::::::::::::/\n:::::::::::::::::::::::::::::::::::::::::::::::::\\ ..............\"~--„_____„„-~~\"\n Also, there's nothing to show right now"
