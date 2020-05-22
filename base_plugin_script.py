import os
import sys

import psutil

from github_menubar import BitBarRenderer
from github_menubar.config import CONFIG, DEFAULT_CONFIG, GLYPHS
from github_menubar.github_client import load_config


def startProcess():
    print(f"{GLYPHS['github_logo']} {GLYPHS['error']} |{CONFIG['font_large']}")
    print("---")
    print(
        'Click to start server |{} bash="/bin/bash" param1="-c" param2="launchctl load -F {}" terminal=false refresh=true'.format(
            CONFIG["font_large"],
            CONFIG['plist_path']
        )
    )

def setup():
    with open(CONFIG["config_file_path"], "w") as f:
        f.write(DEFAULT_CONFIG)
    print(f"{GLYPHS['github_logo']} {GLYPHS['error']}|{CONFIG['font_large']}")
    print("---")
    print(
        f"Click to setup GitHubMenuBar |{CONFIG['font_large']} bash=nano param1={CONFIG['config_file_path']}"
    )


def main(argv):
    if len(argv) == 1:
        try:
            config = load_config()

            if config["user"] is None:
                setup()
                return
        except Exception:
            setup()
            return
        if os.path.exists(CONFIG["pid_file"]):
            with open(CONFIG["pid_file"], "r") as fi:
                pid = int(fi.read().strip())
            if psutil.pid_exists(pid):
                renderer = BitBarRenderer()
                renderer.print_state()
            else:
                startProcess()
        else:
            startProcess()


if __name__ == "__main__":
    main(sys.argv)
