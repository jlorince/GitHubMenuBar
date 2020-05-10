import datetime
import json
import logging
import os
import sys
import time
import webbrowser

from apscheduler.schedulers.background import BackgroundScheduler
import github3
from github3.exceptions import ForbiddenError, NotFoundError
import psutil
import pync
import ZEO
from ZEO.ClientStorage import ClientStorage
from ZODB import DB

# from ZODB.PersistentMapping import PersistentMapping

from github_menubar.config import CONFIG
from github_menubar.utils import load_config, update_config


class GitHubClient:
    def __init__(self) -> None:
        """Initialize the GitHub client and load state from db"""
        self.CONFIG = load_config()
        self.storage = ClientStorage(self.CONFIG["port"])
        self.db = DB(self.storage)
        self._client = github3.login(token=self.CONFIG["token"])
        self._init_db()

    def _init_db(self):
        with self.db.transaction() as conn:
            try:
                conn.root.pull_requests
            except AttributeError:
                conn.root.pull_requests = {}  # PersistentMapping()
                conn.root.notifications = {}  # PersistentMapping()
                conn.root.codeowners = {}  # PersistentMapping()
                conn.root.team_members = {}  # PersistentMapping()
                conn.root.mentioned = set()
                conn.root.team_mentioned = set()
                conn.root.last_update = None

    @classmethod
    def run_server(cls) -> None:
        """Run the GMB server

        Spins up the ZEO database server and a background scheduler to update state
        at the configured interval. Throws an exception if the server is already running.
        """
        if os.path.exists(CONFIG["pid_file"]):
            with open(CONFIG["pid_file"], "r") as fi:
                pid = int(fi.read().strip())
            if psutil.pid_exists(pid):
                raise Exception("Server already running!")
        logging.info("Starting server...")
        config = load_config()
        ZEO.server(path=CONFIG["db_location"], port=config["port"])
        client = cls()
        sched = BackgroundScheduler(daemon=True)
        sched.add_job(
            client.update,
            "interval",
            seconds=config["update_interval"],
            next_run_time=datetime.datetime.now(),
        )
        sched.start()
        with open(CONFIG["pid_file"], "w") as pidfile:
            pidfile.write(str(os.getpid()))
        logging.info("server running")
        try:
            while True:
                time.sleep(2)
        except (KeyboardInterrupt, SystemExit):
            sched.shutdown()

    def get_state(self, complete=False):
        """Get a dictionary specifying the current database state

        By default, excludes the following:
         - muted PRs and associated notifications
         - cleared notifications
         - PRs and associated notifications to be excluded based on the `mentions_only`
           and/or `team_mentions` flags
        If `complete` is True, this will return all notifications/PRs.

        Args:
            complete: If True, return all data, ignoring the `mentions_only and
                `team_mentions` flags
        Returns:
            A dictionary of the complete database state, with the following keys:
            {
                "notifications":
                "pull_requests":
                "codeowners":
                "team_members":
                "last_update":
                "mentioned":
                "team_mentioned":
            }

        """
        mentions_only = False if complete else self.CONFIG["mentions_only"]
        with self.db.transaction() as conn:
            pull_requests = conn.root.pull_requests
            notifications = conn.root.notifications
            if mentions_only:
                pull_requests = {
                    pr_id: pr
                    for pr_id, pr in pull_requests.items()
                    if (pr_id in conn.root.mentioned)
                    or (pr["author"] == self.CONFIG["user"])
                    or (
                        self.CONFIG["team_mentions"]
                        and pr_id in conn.root.team_mentioned
                    )
                }
                notifications = {
                    notif_id: notif
                    for notif_id, notif in notifications.items()
                    if notif.get("pr_id") in conn.root.mentioned
                    or pull_requests.get(notif.get("pr_id"), {}).get("author")
                    == self.CONFIG["user"]
                }
            if not complete:
                pull_requests = {
                    pr_id: pr for pr_id, pr in pull_requests.items() if not pr["muted"]
                }
                notifications = {
                    notif_id: notif
                    for notif_id, notif in notifications.items()
                    if not pull_requests.get(notif.get("pr_id"), {}).get("muted")
                    and not notif["cleared"]
                }

            return {
                "notifications": notifications,
                "pull_requests": pull_requests,
                "codeowners": conn.root.codeowners,
                "team_members": conn.root.team_members,
                "last_update": conn.root.last_update,
                "mentioned": conn.root.mentioned,
                "team_mentioned": conn.root.team_mentioned,
            }

    def _transform_pr_url(self, api_url):
        """Transform a pull request API URL to a browser URL"""
        return api_url.replace("api.github.com/repos", "github.com").replace(
            "/pulls/", "/pull/"
        )

    def rate_limit(self):
        """Get rate limit information from the github3 client"""
        return self._client.rate_limit()

    def get_muted_prs(self) -> dict:
        """Retrieve information on all PRs the user has muted"""
        with self.db.transaction() as conn:
            return [pr for pr in conn.root.pull_requests.values() if pr["muted"]]

    def mute_pr(self, id_) -> None:
        """Mute a PR"""
        with self.db.transaction() as conn:
            pull_requests = conn.root.pull_requests
            pull_requests[id_]["muted"] = True
            conn.root.pull_requests = pull_requests

    def unmute_pr(self, id_):
        """Unmute a PR"""
        with self.db.transaction() as conn:
            pull_requests = conn.root.pull_requests
            pull_requests[id_]["muted"] = False
            conn.root.pull_requests = pull_requests

    def clear_notification(self, notif_id):
        with self.db.transaction() as conn:
            notifications = conn.root.notifications
            notifications[notif_id]["cleared"] = True
            conn.root.notifications = notifications

    def clear_all_notifications(self):
        with self.db.transaction() as conn:
            notifications = conn.root.notifications
            for notif_id, notif in notifications.items():
                notifications[notif_id]["cleared"] = True
            conn.root.notifications = notifications

    def open_notification(self, notif_id):
        self.clear_notification(notif_id)
        with self.db.transaction() as conn:
            webbrowser.open(conn.root.notifications[notif_id]["pr_url"])

    def get_pull_requests(self):
        """Search for all pull_requests involving the user"""
        with self.db.transaction() as conn:
            user_teams = [
                team
                for repo, teams in conn.root.team_members.items()
                for team, members in teams.items()
                if self.CONFIG["user"] in members
            ]
        prs = []
        issue_pr_map = {}
        for issue in self._client.search_issues(
            f"is:open is:pr involves:{self.CONFIG['user']} archived:false"
        ):
            pr = issue.issue.pull_request()
            issue_pr_map[issue.id] = pr.id
            prs.append(pr)

        for issue in self._client.search_issues(
            f"is:open is:pr mentions:{self.CONFIG['user']} archived:false"
        ):
            with self.db.transaction() as conn:
                mentioned = conn.root.mentioned
                mentioned.add(issue_pr_map[issue.id])
                conn.root.mentioned = mentioned
        for team in user_teams:
            for issue in self._client.search_issues(
                f"is:open is:pr team:{team} archived:false"
            ):
                if issue.id not in issue_pr_map:
                    pr = issue.issue.pull_request()
                    prs.append(pr)
                    issue_pr_map[issue.id] = pr.id
                with self.db.transaction() as conn:
                    team_mentioned = conn.root.team_mentioned
                    team_mentioned.add(issue_pr_map[issue.id])
                    conn.root.team_mentioned = team_mentioned

        return prs

    def _notify(self, **kwargs):
        """Trigger a desktop notification (if they are enabled)"""
        if self.CONFIG["desktop_notifications"]:
            pync.notify(**kwargs)

    def _parse_notification(self, notification, prs_by_url):
        notif = notification.subject.copy()
        comment_url = notif.get("latest_comment_url", "")
        if comment_url and "comments" in comment_url:
            notif["comment"] = json.loads(
                self._client._get(comment_url).content.decode()
            )
        notif["cleared"] = False
        return notif

    def _parse_pr_from_notification(self, notification):
        url = notification.subject["url"]
        url_info = url.replace("https://api.github.com/repos/", "").split("/")
        pr = self._client.pull_request(url_info[0], url_info[1], int(url_info[3]))
        parsed = self.parse_pull_request(pr, get_test_status=False)
        with self.db.transaction() as conn:
            pull_requests = conn.root.pull_requests
            pull_requests[pr.id] = parsed
            conn.root.pull_requests = pull_requests
        self.current_prs.add(pr.id)
        return parsed

    def _get_full_repo(self, pull_request):
        short_repo = pull_request.repository
        return self._client.repository(short_repo.owner.login, short_repo.name)

    def _get_protection(self, pull_request):
        full_repo = self._get_full_repo(pull_request)
        return full_repo.branch(pull_request.base.ref).original_protection

    def _update_pull_requests(self):
        self.protection = {}
        for pull_request in self.get_pull_requests():
            repo = pull_request.repository
            repo_key = f"{repo.owner.login}|{repo.name}"
            if pull_request.base.ref not in self.protection:
                self.protection[pull_request.base.ref] = self._get_protection(
                    pull_request
                )
            with self.db.transaction() as conn:
                codeowners = conn.root.codeowners
                if repo_key not in codeowners:
                    try:
                        codeowner_file = pull_request.repository.file_contents(
                            "CODEOWNERS"
                        )
                        codeowner_file_contents = codeowner_file.decoded.decode()
                        codeowners[repo_key] = self.parse_codeowners_file(
                            codeowner_file_contents
                        )
                    except (NotFoundError, ForbiddenError):
                        codeowners[repo_key] = None
                    conn.root.codeowners = codeowners
            with self.db.transaction() as conn:
                team_members = conn.root.team_members
                if repo.owner.login not in team_members:
                    try:
                        org = self._client.organization(repo.owner.login)
                        team_members[repo.owner.login] = self.parse_teamembers(org)
                    except (NotFoundError, ForbiddenError):
                        team_members[repo.owner.login] = None
                conn.root.team_members = team_members

            parsed = self.parse_pull_request(pull_request)
            with self.db.transaction() as conn:
                conn.root.pull_requests[pull_request.id] = parsed
            self.current_prs.add(pull_request.id)

    def _should_notify(self, notif):
        id_ = notif["pr_id"]
        with self.db.transaction() as conn:
            if conn.root.pull_requests[id_]["muted"]:
                return False
        if self.CONFIG["mentions_only"] and self.CONFIG["team_mentions"]:
            with self.db.transaction() as conn:
                return id_ in conn.root.mentioned or id_ in conn.root.team_mentioned
        if self.CONFIG["mentions_only"] and not self.CONFIG["team_mentions"]:
            with self.db.transaction() as conn:
                return id_ in conn.root.mentioned
        return True

    def _update_notifications(self, mentions_only=False):
        with self.db.transaction() as conn:
            prs_by_url = {pr["url"]: pr for pr in conn.root.pull_requests.values()}
        for notification in self._client.notifications():
            notif_id = int(notification.id)
            self.current_notifications[int(notification.id)] = notification
            with self.db.transaction() as conn:
                new = notif_id not in conn.root.notifications
            if new:
                parsed = self._parse_notification(notification, prs_by_url)
            else:
                with self.db.transaction() as conn:
                    parsed = conn.root.notifications[notif_id]
                    if conn.root.notifications[notif_id]["cleared"]:
                        notification.mark()

            corresponding_pr = prs_by_url.get(notification.subject["url"])
            if (
                corresponding_pr is None
                or corresponding_pr["id"] not in self.current_prs
            ) and parsed["type"] == "PullRequest":
                corresponding_pr = self._parse_pr_from_notification(notification)
            parsed["pr_id"] = corresponding_pr["id"] if corresponding_pr else None
            parsed["pr_url"] = (
                corresponding_pr["browser_url"] if corresponding_pr else None
            )
            if new and self._should_notify(parsed):
                self._notify(
                    title="New Notification",
                    message=f"\{notification.subject['title']}",
                    open=parsed["pr_url"],
                )

            with self.db.transaction() as conn:
                conn.root.notifications[notif_id] = parsed

    def update(self):
        self.current_notifications = {}
        self.current_prs = set()
        self._update_pull_requests()
        self._update_notifications(mentions_only=load_config()["mentions_only"])
        # clear any old notifications
        with self.db.transaction() as conn:
            conn.root.notifications = {
                id_: notif
                for id_, notif in conn.root.notifications.items()
                if id_ in self.current_notifications
            }
            # clear any old pull requests
            conn.root.pull_requests = {
                pr["id"]: pr
                for pr in conn.root.pull_requests.values()
                if pr["id"] in self.current_prs
            }
        with self.db.transaction() as conn:
            conn.root.last_update = time.time()
        self.db.pack()

    def parse_codeowners_file(self, file_contents):
        codeowners = []
        for line in file_contents.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                path, owners = line.split(maxsplit=1)
                codeowners.append(
                    (path, tuple(sorted(owners.replace("@", "").split())))
                )
        return codeowners

    def parse_teamembers(self, org):
        team_members = {}
        for team in org.teams():
            members = [member.login for member in team.members()]
            team_name = "-".join(team.name.lower().split())
            team_members[f"{org.login}/{team_name}"] = members
        return team_members

    def get_pr_codeowners(self, pr, reviews):
        all_owners = {}
        with self.db.transaction() as conn:
            codeowner_info = conn.root.codeowners.get(
                f"{pr.repository.owner.login}|{pr.repository.name}"
            )
        if codeowner_info:
            for file in pr.files():
                file_owners = None
                for path, owners in codeowner_info:
                    if path == "*":
                        file_owners = owners
                    if path in f"/{file.filename}":
                        file_owners = owners
                if file_owners and file_owners not in all_owners:
                    approved = False
                    if reviews:
                        for owner in file_owners:
                            if "/" in owner:
                                with self.db.transaction() as conn:
                                    if any(
                                        user
                                        in conn.root.team_members.get(
                                            pr.repository.owner.login, {}
                                        ).get(owner, ())
                                        and review["state"] == "APPROVED"
                                        for user, review in reviews.items()
                                    ):
                                        approved = True
                                        break
                            else:
                                if any(
                                    user == owner
                                    and review["state"] == "APPROVED"
                                    for user, review in reviews.items()
                                ):
                                    approved = True
                                    break

                    all_owners["|".join(file_owners)] = approved
        return all_owners

    def parse_reviews(self, pull_request):
        reviews = {}
        for review in pull_request.reviews():
            # if review.user.login != self.CONFIG["user"]:
            reviews[review.user.login] = {"state": review.state}
        return reviews

    def _format_pr_description(self, pull_request):
        return (
            f"{pull_request.repository.owner.login}/{pull_request.repository.name} "
            f"{pull_request.number}: {pull_request.title}"
        )

    def parse_pull_request(self, pull_request, get_test_status=True):
        reviews = self.parse_reviews(pull_request)
        with self.db.transaction() as conn:
            previous = conn.root.pull_requests.get(pull_request.id, {})
        parsed = {
            "base": pull_request.base.ref,
            "head": pull_request.head.ref,
            "mergeable": pull_request.mergeable,
            "mergeable_state": pull_request.mergeable_state,
            "description": self._format_pr_description(pull_request),
            "state": "MERGED" if pull_request.merged else pull_request.state.upper(),
            "url": pull_request.url,
            "browser_url": pull_request.html_url,
            "author": pull_request.user.login,
            "updated_at": str(pull_request.updated_at),
            "reviews": reviews,
            "muted": previous.get("muted", False),
            "id": pull_request.id,
            "last_modified": pull_request.last_modified,
            "repo": pull_request.repository.name,
            "org": pull_request.repository.owner.login,
            "protected": self.protection.get(pull_request.base.ref, {}).get(
                "enabled", False
            ),
            "title": pull_request.title,
            "number": pull_request.number,
        }
        parsed["test_status"] = (
            {}
            if pull_request.merged or not get_test_status
            else self._get_test_status(pull_request)
        )
        parsed["owners"] = self.get_pr_codeowners(pull_request, reviews)

        if (
            previous
            and parsed["author"] == self.CONFIG["user"]
            and parsed["test_status"]
        ):
            self._state_change_notification(parsed, previous)
        return parsed

    def _state_change_notification(self, current_pr, previous_pr):
        if (current_pr["test_status"]["outcome"] != "pending") and (
            previous_pr["test_status"]["outcome"]
            != current_pr["test_status"]["outcome"]
        ):
            self._notify(
                title="Test status change",
                subtitle=f"{current_pr['description']}",
                message=f"{current_pr['test_status']['outcome']}",
                open=current_pr["browser_url"],
            )
        if (
            current_pr["mergeable_state"] == "dirty"
            and previous_pr["mergeable_state"] != "dirty"
        ):
            self._notify(
                title="Merge conflict",
                message=f"{current_pr['description']}",
                open=current_pr["browser_url"],
            )

    def _get_test_status(self, pull_request):
        repo = self._get_full_repo(pull_request)
        commit = repo.commit(repo.branch(pull_request.head.ref).latest_sha())
        protected = self.protection[pull_request.base.ref]["enabled"]
        in_progress = False
        suite_outcome = None
        runs = {}
        conclusions = set()
        for check in commit.check_runs():
            required = check.name in self.protection[pull_request.base.ref][
                "required_status_checks"
            ].get("contexts", [])
            runs[check.name] = (check.conclusion, required)
            if required:
                if check.status == "completed":
                    conclusions.add(check.conclusion)
                else:
                    in_progress = True
        if in_progress:
            suite_outcome = "in_progress"
        if protected and conclusions:
            if (
                "failure" in conclusions
                or "timed_out" in conclusions
                or "action_required" in conclusions
            ):
                suite_outcome = "failure"
            elif "cancelled" in conclusions:
                suite_outcome = "cancelled"
            else:
                suite_outcome = "success"
        return {"outcome": suite_outcome if protected else None, "runs": runs}


def main():
    if len(sys.argv) == 1:
        GitHubClient.run_server()
    if sys.argv[1] == "open":
        client = GitHubClient()
        client.open_notification(int(sys.argv[2]))
    if sys.argv[1] == "clear":
        client = GitHubClient()
        client.clear_notification(int(sys.argv[2]))
    if sys.argv[1] == "clearall":
        GitHubClient().clear_all_notifications()
    if sys.argv[1] == "mute":
        client = GitHubClient()
        client.mute_pr(int(sys.argv[2]))
    if sys.argv[1] == "unmute":
        client = GitHubClient()
        client.unmute_pr(int(sys.argv[2]))
    if sys.argv[1] == "config":
        update_config(sys.argv[2], sys.argv[3])
    if sys.argv[1] == "refresh":
        client = GitHubClient()
        client.update()
