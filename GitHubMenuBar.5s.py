#!/usr/bin/env PYTHONIOENCODING=UTF-8 /usr/bin/python
import os
import subprocess
import sys

from dotenv import load_dotenv  # noqa: I100

# Need to load the env before importing `CONFIG`
load_dotenv()  # noqa: I100

from github_menubar import BitBarRenderer, CONFIG

import psutil


PID_FILE = CONFIG["pid_file"]


def startProcess():
    print(
        f"{CONFIG['glyphs']['github_logo']} GMB Server loading...|{CONFIG['font_large']}"
    )
    process = subprocess.Popen(
        [f"{sys.executable.rsplit('/', 1)[0]}/gmb-server"],
        env=os.environ.copy(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    with open(PID_FILE, "w") as fi:
        fi.write(str(process.pid))


if __name__ == "__main__":

    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as fi:
            pid = int(fi.read().strip())
        if psutil.pid_exists(pid):
            renderer = BitBarRenderer(pid)
            renderer.print_state()
        else:
            startProcess()
    else:
        startProcess()
