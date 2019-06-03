#!/usr/bin/env PYTHONIOENCODING=UTF-8 /Users/jlorince/anaconda3/bin/python
import os
import sys
from subprocess import call

from github_menubar import BitBarRenderer, CONFIG

PID_FILE = "/tmp/github_menubar.pid"

if __name__ == "__main__":
    if os.path.exists(PID_FILE):
        renderer = BitBarRenderer()
        renderer.print_state()
    else:
        call(
            [
                sys.executable.replace("python", "gunicorn"),
                "--bind",
                f"localhost:{CONFIG['port']}",
                "github_menubar.wsgi",
                "--daemon",
                "-p",
                PID_FILE,
            ]
        )
