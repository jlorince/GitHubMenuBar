#!/usr/bin/env PYTHONIOENCODING=UTF-8 /usr/bin/python
from dotenv import load_dotenv
# Need to load the env before importing `CONFIG`
load_dotenv()
import os
import subprocess
import sys
from github_menubar import BitBarRenderer, CONFIG
import psutil


PID_FILE = CONFIG["pid_file"]


def startProcess():
    process = subprocess.Popen(
        [f"{sys.executable.rsplit('/', 1)[0]}/gmb-server"], env=os.environ.copy()
    )
    # Write PID file
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
            sys.exit()
    else:
        startProcess()
        sys.exit()
