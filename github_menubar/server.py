import datetime
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from flask import Flask, jsonify, redirect, request

from github_menubar import CONFIG, GitHubClient, TREX


def main():

    logging.basicConfig(
        filename="/tmp/gitmnubar.log",
        filemode="a",
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
    )
    logging.info("starting logging")

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

    @app.route("/clear_notification")
    def clear_notification():
        """unmute a pr"""
        app.client.clear_notification(int(request.args.get("notif")))
        return redirect(request.args.get("redirect"))

    @app.route("/refresh")
    def refresh():
        """Force a full refresh"""
        app.client.update()
        return "ok"

    app.run(port=CONFIG["port"], threaded=True)


if __name__ == "__main__":
    main()
