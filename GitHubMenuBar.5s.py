#!/usr/bin/env PYTHONIOENCODING=UTF-8 /usr/bin/python
import json
import os
import subprocess
import sys

from github_menubar import BitBarRenderer
from github_menubar.config import CONFIG, GLYPHS, HELP_MESSAGE
from github_menubar.github_client import load_config

import psutil


def startProcess():
    print(
        f"{GLYPHS['github_logo']} GMB Server loading...|{CONFIG['font_large']}"
    )
    process = subprocess.Popen(
        [f"{sys.executable.rsplit('/', 1)[0]}/gmb-server"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    with open(CONFIG["pid_file"], "w") as fi:
        fi.write(str(process.pid))


def setup():
    with open(CONFIG["config_file_path"], "w") as f:
        f.write(f"{HELP_MESSAGE}")
        f.write(json.dumps(CONFIG, indent=4))
    print(f"{GLYPHS['github_logo']} |{CONFIG['font_large']}")
    print("---")
    print(f"Click to setup GitHubMenuBar |{CONFIG['font_large']} bash=$EDITOR param1={CONFIG['config_file_path']}")


def main(argv):
    if len(argv) == 1:
        try:
            config = load_config()
            if config["user"] is None:
                setup()
                return
        except FileNotFoundError:
            setup()
            return
        if os.path.exists(config["pid_file"]):
            with open(config["pid_file"], "r") as fi:
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

