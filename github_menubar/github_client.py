import json
import logging
import time

import github3
from github3.exceptions import NotFoundError

from github_menubar.config import CONFIG as DEFAULT_CONFIG

import pync


def load_config():
    config_file_content = open(DEFAULT_CONFIG["config_file_path"]).read()
    json_content = config_file_content.split(
        "##### DO NOT DELETE OR MODIFY THIS LINE #####"
    )[1].strip()
    return json.loads(json_content)


CONFIG = load_config()


class GitHubClient:
    def __init__(self):
        """Initialize the GitHub client and load state from disk"""
        self._client = github3.login(token=CONFIG["token"])
        try:
            self._load_state()
        except Exception:
            self.notifications = {}
            self.pull_requests = {}
            self.codeowners = {}
            self.team_members = {}
            self.mentioned = set()
            self.last_update = None
            self.mentions_only = False

    def toggle_mentions_only(self):
        self.mentions_only = not self.mentions_only

    def get_state(self, mentions_only=None):
        """Get the current state as a JSON-serializable dictionary"""
        _mentions_only = (
            mentions_only if mentions_only is not None else self.mentions_only
        )
        if _mentions_only:
            pull_requests = {
                pr_id: pr
                for pr_id, pr in self.pull_requests.items()
                if pr_id in self.mentioned or pr["author"] == CONFIG["user"]
            }
            notifications = {
                notif_id: notif
                for notif_id, notif in self.notifications.items()
                if notif["pr_id"] in self.mentioned
                or self.pull_requests[notif["pr_id"]]["author"] == CONFIG["user"]
            }
        else:
            pull_requests = self.pull_requests
            notifications = self.notifications
        return {
            "notifications": notifications,
            "pull_requests": pull_requests,
            "codeowners": self.codeowners,
            "team_members": self.team_members,
            "last_update": self.last_update,
            "mentioned": list(self.mentioned),
            "mentions_only": self.mentions_only,
        }

    def _dump_state(self):
        """Dump current state to disk"""
        with open(CONFIG["state_path"], "w") as fh:
            fh.write(json.dumps(self.get_state(mentions_only=False)))

    def _transform_pr_url(self, api_url):
        """Transform a pull request API URL to a browser URL"""
        return api_url.replace("api.github.com/repos", "github.com").replace(
            "/pulls/", "/pull/"
        )

    def _load_state(self):
        """load state from disk"""
        with open(CONFIG["state_path"], "r") as fh:
            state = json.loads(fh.read())
            self.notifications = state["notifications"]
            self.pull_requests = state["pull_requests"]
            self.codeowners = state["codeowners"]
            self.team_members = state["team_members"]
            self.last_update = state["last_update"]
            self.mentioned = set(state["mentioned"])
            self.mentions_only = state["mentions_only"]

    def rate_limit(self):
        """Get rate limit information from the github3 client"""
        return self._client.rate_limit()

    def get_muted_prs(self) -> dict:
        """Retrieve information on all PRs the user has muted"""
        return [pr for pr in self.pull_requests.values() if pr["muted"]]

    def mute_pr(self, id_) -> None:
        """Mute a PR"""
        self.pull_requests[id_]["muted"] = True

    def unmute_pr(self, id_):
        """Unmute a PR"""
        self.pull_requests[id_]["muted"] = False

    def clear_notification(self, notif_id):
        self.notifications[notif_id]["cleared"] = True

    def get_pull_requests(self):
        """Search for all pull_requests involving the user"""
        prs = []
        issue_pr_map = {}
        for issue in self._client.search_issues(
            f"is:open is:pr involves:{CONFIG['user']} archived:false"
        ):
            pr = issue.issue.pull_request()
            issue_pr_map[issue.id] = pr.id
            prs.append(pr)

        for issue in self._client.search_issues(
            f"is:open is:pr mentions:{CONFIG['user']} archived:false"
        ):
            self.mentioned.add(issue_pr_map[issue.id])
        return prs

    def _notify(self, message, title=None, url=None):
        """Trigger a desktop notification (if they are enabled)"""
        if CONFIG["desktop_notifications"]:
            pync.notify(message, title=title, open=url)

    def _parse_notification(self, notification):
        prs_by_url = {pr["url"]: pr for pr in self.pull_requests.values()}
        notif = notification.subject.copy()
        comment_url = notif.get("latest_comment_url", "")
        if comment_url and "comments" in comment_url:
            comment_info = json.loads(self._client._get(comment_url).content.decode())
            notif["comment"] = comment_info["body_text"]
        notif["cleared"] = False
        corresponding_pr = prs_by_url.get(notification.subject["url"])
        notif["pr_id"] = corresponding_pr["id"] if corresponding_pr else None
        notif["pr_url"] = corresponding_pr["browser_url"]
        return notif

    def _update_pull_requests(self):
        pull_requests = []
        for pull_request in self.get_pull_requests():
            repo = pull_request.repository
            repo_key = f"{repo.owner.login}|{repo.name}"
            if repo_key not in self.codeowners:
                try:
                    codeowner_file = pull_request.repository.file_contents("CODEOWNERS")
                    codeowner_file_contents = codeowner_file.decoded.decode()
                    self.codeowners[repo_key] = self.parse_codeowners_file(
                        codeowner_file_contents
                    )
                except NotFoundError:
                    self.codeowners[repo_key] = None
            if repo.owner.login not in self.team_members:
                try:
                    org = self._client.organization(repo.owner.login)
                    self.team_members[repo.owner.login] = self.parse_teamembers(org)
                except NotFoundError:
                    self.team_members[repo.owner.login] = None

            pull_requests.append(pull_request)

        for pr in pull_requests:
            self.pull_requests[pr.id] = self.parse_pull_request(pr)
        # clear any old pull requests
        current_pr_ids = {pr.id for pr in pull_requests}
        self.pull_requests = {
            pr["id"]: pr
            for pr in self.pull_requests.values()
            if pr["id"] in current_pr_ids
        }

    def _update_notifications(self):
        current_notifications = set()
        for notification in self._client.notifications():
            current_notifications.add(notification.id)
            if notification.id not in self.notifications:
                parsed = self._parse_notification(notification)
                self.notifications[notification.id] = parsed
                if not self.mentions_only or notification["pr_id"] in self.mentioned:
                    self._notify(
                        title="New Notification",
                        message=notification.subject["title"],
                        url=parsed["pr_url"],
                    )
        # clear any old notifications
        self.notifications = {
            id_: notif
            for id_, notif in self.notifications.items()
            if id_ in current_notifications
        }

    def update(self):
        self.codeowners = {}
        self.team_members = {}
        logging.info(CONFIG["token"])
        logging.info("starting update")
        self._update_pull_requests()
        logging.info("done with update")
        self._update_notifications()
        self._dump_state()
        self.last_update = time.time()

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
        for file in pr.files():
            for path, owners in self.codeowners.get(
                f"{pr.repository.owner.login}|{pr.repository.name}", []
            ):
                if path in f"/{file.filename}":
                    if owners not in all_owners:
                        approved = False
                        if reviews:
                            for owner in owners:
                                if "/" in owner:
                                    if any(
                                        user
                                        in self.team_members.get(
                                            pr.repository.owner.login, {}
                                        ).get(owner, ())
                                        and review["state"] == "APPROVED"
                                        for user, review in reviews.items()
                                    ):
                                        approved = True
                                        break
                                else:
                                    if any(
                                        user == owner and review["state"] == "APPROVED"
                                        for user, review in reviews.items()
                                    ):
                                        approved = True
                                        break
                        all_owners["|".join(owners)] = approved
        return all_owners

    def parse_reviews(self, pull_request):
        reviews = {}
        for review in pull_request.reviews():
            if review.user.login != CONFIG["user"]:
                reviews[review.user.login] = {"state": review.state}
        return reviews

    def _format_pr_description(self, pull_request):
        return (
            f"{pull_request.repository.owner.login}/{pull_request.repository.name} "
            f"{pull_request.number}: {pull_request.title}"
        )

    def parse_pull_request(self, pull_request):
        reviews = self.parse_reviews(pull_request)
        previous = self.pull_requests.get(pull_request.id, {})
        parsed = {
            "mergeable": pull_request.mergeable,
            "mergeable_state": pull_request.mergeable_state,
            "description": self._format_pr_description(pull_request),
            "state": "MERGED" if pull_request.merged else pull_request.state.upper(),
            "url": pull_request.url,
            "browser_url": pull_request.html_url,
            "author": pull_request.user.login,
            "test_status": self._get_test_status(pull_request),
            "updated_at": str(pull_request.updated_at),
            "reviews": reviews,
            "muted": previous.get("muted", False),
            "id": pull_request.id,
        }
        parsed["owners"] = self.get_pr_codeowners(pull_request, reviews)

        if previous and parsed["author"] == CONFIG["user"]:
            self._state_change_notification(parsed, previous)
        return parsed

    def _state_change_notification(self, current_pr, previous_pr):
        if previous_pr["test_status"] != current_pr["test_status"]:
            self._notify(
                title="Test status change",
                message=f"{current_pr['description']}: {current_pr['test_status']}",
                url=current_pr["browser_url"],
            )
        if previous_pr["mergeable"] and not current_pr["mergeable"]:
            self._notify(
                title="Merge conflict",
                message=f"{current_pr['description']}",
                url=current_pr["browser_url"],
            )

    def _get_test_status(self, pull_request):
        # Get last commit
        # TODO - is there a way we can just get the most recent one?
        commit = None
        for commit in pull_request.commits():
            pass
        try:
            commit.check_suites().next()
            test_status = "pending"
        except StopIteration:
            test_status = None
        for check in commit.check_runs():
            if check.name == "pull-request-tests":
                test_status = check.conclusion
                break
        return test_status
