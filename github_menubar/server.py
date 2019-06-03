import argparse
import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from flask import Flask, jsonify, request

from github_menubar import CONFIG, GitHubClient, TREX


def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


app = Flask(__name__)
app.client = GitHubClient()


def update():
    app.client.update()


sched = BackgroundScheduler(daemon=True)
sched.add_job(
    update,
    "interval",
    seconds=CONFIG["update_interval"],
    next_run_time=datetime.datetime.now(),
)
sched.start()


@app.route("/state")
def get_state():
    """Main endpoint to get the state of the GitHubClient"""
    return jsonify(app.client.get_state())


@app.route("/muted")
def get_muted_prs():
    """Get a listing of all muted prs"""
    return jsonify(app.client.get_muted_prs())


@app.route("/trex")
def trex():
    """Roar!"""
    return TREX


@app.route("/mute_pr")
def mute_pr():
    """Mute a pr"""
    app.client.mute_pr(int(request.args.get("pr")))
    return "ok"


@app.route("/unmute_pr")
def unmute_pr():
    """unmute a pr"""
    app.client.unmute_pr(int(request.args.get("pr")))
    return "ok"


@app.route("/refresh")
def refresh():
    """Force a full refresh"""
    app.client.update()
    return "ok"


def main():
    parser = argparse.ArgumentParser(
        description="Interface for the GitHubMenubar server"
    )
    parser.add_argument(
        "--start",
        action="store_true",
        help="start the server; this is a no-op if the server is already running",
    )
    parser.add_argument("--stop", action="store_true", help="stop the server")
    parser.add_argument("--restart", action="store_true", help="restart the server")
    args = parser.parse_args()
    if args.start:
        daemon = Daemonize(app="GitHubMenubar", pid=PID_FILE, action=run_server)
        daemon.start()
        sys.exit()
    elif args.stop:
        try:
            requests.post(f"http://127.0.0.1:{CONFIG['port']}/shutdown")
        except requests.ConnectionError:
            pass


if __name__ == "__main__":
    app.client = GitHubClient()
    app.run(port=CONFIG["port"])
    # daemon = Daemonize(app="GitHubMenubar", pid=PID_FILE, action=run_server)
    # daemon.start()
