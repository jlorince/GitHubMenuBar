import json
from datetime import datetime

import requests

from tabulate import tabulate

from github_menubar.config import COLORS, GLYPHS
from github_menubar.github_client import load_config

REVIEW_STATE_MAP = {
    "COMMENTED": "comment",
    "APPROVED": "success",
    "CHANGES_REQUESTED": "error",
    "DISMISSED": "x",
}
TEST_STATUS_MAP = {
    "pending": "in_progress",
    "success": "success",
    "failure": "error",
    "cancelled": "cancelled",
    "neutral": "in_progress",
}

MAX_LENGTH = 100
MAX_PR_LENGTH = 60

CONFIG = load_config()
PID = int(open(CONFIG["pid_file"]).read().strip())


def _trimmer(text):
    if len(text) > MAX_PR_LENGTH:
        return f"{text[:MAX_PR_LENGTH]}..."
    return text


def chunkstring(string, length):
    return (string[0 + i : length + i] for i in range(0, len(string), length))


class Renderer:
    """Base class for renderers

    Implements generic renderer functionality.
    """

    def __init__(self):
        self.state = self._get_state()
        self.muted_prs = self._get_muted_prs()
        self.error = False

    def _get_state(self):
        response = requests.get(f"http://127.0.0.1:{CONFIG['port']}/state")
        state = json.loads(response.content)
        for id_ in list(state["pull_requests"]):
            state["pull_requests"][int(id_)] = state["pull_requests"].pop(id_)
        return state

    def _get_muted_prs(self):
        response = requests.get(f"http://127.0.0.1:{CONFIG['port']}/muted")
        return json.loads(response.content)

    def transform_pr_url(self, api_url):
        return api_url.replace("api.github.com/repos", "github.com").replace(
            "/pulls/", "/pull/"
        )

    @property
    def _user_prs(self):
        for pull_request in self.state["pull_requests"].values():
            if pull_request["author"] == CONFIG["user"] and not pull_request["muted"]:
                yield pull_request

    @property
    def _involved_prs(self):
        for pull_request in self.state["pull_requests"].values():
            if pull_request["author"] != CONFIG["user"] and not pull_request["muted"]:
                yield pull_request

    @property
    def _pr_urls(self):
        return {pr["url"]: pr for pr in self.state["pull_requests"].values()}


class BitBarRenderer(Renderer):
    def _build_notification_pr_table(self):
        rows = []
        ids = []
        notif_ids = []
        for notif_id, notification in self.state["notifications"].items():
            if not notification["cleared"] and notification["url"] in self._pr_urls:
                pr = self._pr_urls[notification["url"]]
                rows.append(
                    [
                        _trimmer(pr["description"]),
                        pr["author"],
                        pr["state"],
                        notification.get("comment", ""),
                    ]
                )
                ids.append(pr["id"])
                notif_ids.append(notif_id)
        return (
            tabulate(
                rows, headers=["PR", "author", "state", ""], tablefmt="plain"
            ).split("\n"),
            ids,
            notif_ids
        )

    def _colorize_pr(self, pull_request):
        if pull_request["state"] == "CLOSED":
            color = "gray"
        elif (
            pull_request["test_status"] == "failure"
            or pull_request["mergeable"] is False
        ):
            color = COLORS["red"]
        elif pull_request["mergeable_state"] != "blocked":
            color = COLORS["green"]
        else:
            color = COLORS["orange"]
        return color

    def _build_pr_table(self, prs):
        rows = []
        ids = []
        for pull_request in prs:
            merge_conflict = (
                GLYPHS["success"] if pull_request["mergeable"] else GLYPHS["error"]
            )
            approved = GLYPHS["in_progress"]
            if pull_request["owners"]:
                if all(pull_request["owners"].values()):
                    approved = GLYPHS["success"]
            else:
                if any(
                    review["state"] == "APPROVED"
                    for review in pull_request["reviews"].values()
                ):
                    approved = GLYPHS["success"]

            test_status = (
                GLYPHS["na"]
                if pull_request["test_status"] is None
                else GLYPHS[TEST_STATUS_MAP[pull_request["test_status"]]]
            )
            rows.append(
                [
                    _trimmer(pull_request["description"]),
                    merge_conflict,
                    test_status,
                    approved,
                ]
            )
            ids.append(pull_request["id"])
        return (
            tabulate(
                rows,
                headers=[
                    "description",
                    GLYPHS["merged_pr"],
                    GLYPHS["tests"],
                    GLYPHS["approval"],
                ],
                tablefmt="plain",
            ).split("\n"),
            ids,
        )

    def _build_codeowners_tables(self, prs):
        result = []
        for pr in prs:
            rows = []
            colors = []
            if not pr["owners"]:
                result.append(None)
                continue
            for owners, approved in pr["owners"].items():
                formatted_owners = ", ".join(
                    owner.split("/", 1)[-1] for owner in owners.split("|")
                )
                colors.append(COLORS["green"] if approved else COLORS["orange"])
                rows.append(
                    [
                        formatted_owners,
                        GLYPHS["success"] if approved else GLYPHS["in_progress"],
                    ]
                )
            result.append((tabulate(rows, tablefmt="plain").split("\n"), colors))
        return result

    def _build_review_tables(self, prs):
        result = []
        for pr in prs:
            rows = []
            for user, review in pr["reviews"].items():
                glyph = GLYPHS[REVIEW_STATE_MAP[review["state"]]]
                rows.append([user, glyph])
            result.append(tabulate(rows, tablefmt="plain").split("\n"))
        return result

    def _get_header_info(self):
        n_notifications = len(
            [
                notif
                for notif in self.state["notifications"].values()
                if not notif["cleared"] and notif["url"] in self._pr_urls
            ]
        )
        n_failing_tests = 0
        n_open_prs = 0
        n_merge_conflicts = 0
        n_ready = 0
        for pr in self.state["pull_requests"].values():
            if pr["author"] == CONFIG["user"]:
                n_open_prs += 1
                if pr["test_status"] == "failure":
                    n_failing_tests += 1
                if not pr["mergeable"]:
                    n_merge_conflicts += 1
                if pr["mergeable_state"] != "blocked":
                    n_ready += 1
        return {
            "n_notifications": n_notifications,
            "n_failing_tests": n_failing_tests,
            "n_open_prs": n_open_prs,
            "n_merge_conflicts": n_merge_conflicts,
            "n_ready": n_ready,
        }

    def _build_header(
        self, n_notifications, n_open_prs, n_failing_tests, n_merge_conflicts, n_ready
    ):
        result = f"{GLYPHS['github_logo']} "
        if CONFIG["collapsed"]:
            return result
        if n_notifications:
            result += f"{GLYPHS['bell']}{n_notifications} "
        if n_open_prs:
            result += f"{GLYPHS['open_pr']}{n_open_prs} "
        if n_failing_tests:
            result += f"{GLYPHS['tests']}{n_failing_tests} "
        if n_merge_conflicts:
            result += f"{GLYPHS['merged_pr']}{n_merge_conflicts} "
        if n_ready:
            result += f"{GLYPHS['success']}{n_ready} "
        return result

    def _printer(
        self,
        string,
        indent=0,
        font=CONFIG["font"],
        color=None,
        href=None,
        refresh=False,
        alternate=False,
        bash=None,
        param1=None,
        param2=None,
        open_terminal=False,
    ):
        if string is not None:
            result = f"{'--' * indent}{string}|{font} length={MAX_LENGTH}"
            if color:
                result += f" color={color}"
            if href:
                result += f" href={href}"
            if refresh:
                result += " refresh=true"
            if alternate:
                result += " alternate=true"
            if bash:
                result += f" bash={bash} terminal={str(open_terminal).lower()}"
            if param1:
                result += f" param1={param1}"
            if param2:
                result += f" param2={param2}"
            print(result)

    def _section_break(self, indent=0):
        print(f"{'--' * indent}---")

    def print_state(self):
        if self.error:
            self._printer(GLYPHS["github_logo"])
            self._section_break()
            self._printer("No connection")
        else:
            header_info = self._get_header_info()
            header = self._build_header(**header_info)
            self._printer(header, font=CONFIG["font_large"])
            self._section_break()
            self._printer("SUMMARY")
            self._printer(
                f"{GLYPHS['bell']} Notifications: {header_info['n_notifications']}",
                href="https://github.com/notifications",
            )
            self._printer(
                f"{GLYPHS['open_pr']} Open Pull Requests: {header_info['n_open_prs']}",
                href="https://github.com/pulls",
            )
            self._printer(
                f"{GLYPHS['tests']} Failing tests: {header_info['n_failing_tests']}",
                indent=1,
            )
            self._printer(
                f"{GLYPHS['merged_pr']} Merge Conflicts: {header_info['n_merge_conflicts']}",
                indent=1,
            )
            self._printer(
                f"{GLYPHS['success']} Mergeable: {header_info['n_ready']}", indent=1
            )
            self._section_break()
            if len(self.state["pull_requests"]) == 0:
                self._printer(TREX)
            else:
                notif_pr_table, pr_ids, notif_ids = self._build_notification_pr_table()
                if len(notif_pr_table) > 1:
                    self._printer("NOTIFICATIONS")
                    self._printer(notif_pr_table[0])
                    for row, pr_id, notif_id in zip(notif_pr_table[1:], pr_ids, notif_ids):
                        self._printer(
                            row,
                            href='"http://localhost:{}/clear_notification?notif={}&redirect={}"'.format(
                                CONFIG["port"],
                                notif_id,
                                self.state["pull_requests"][pr_id]["browser_url"],
                            ),
                            refresh=True,
                        )
                user_pr_table, ids = self._build_pr_table(self._user_prs)
                codeowner_info = self._build_codeowners_tables(self._user_prs)
                review_info = self._build_review_tables(self._user_prs)
                if len(user_pr_table) > 1:
                    self._section_break()
                    self._printer("MY PULL REQUESTS")
                    self._printer(user_pr_table[0])
                    for row, id_, codeowners, reviews in zip(
                        user_pr_table[1:], ids, codeowner_info, review_info
                    ):
                        pull_request = self.state["pull_requests"][id_]
                        self._printer(
                            row,
                            color=self._colorize_pr(pull_request),
                            href=pull_request["browser_url"],
                        )
                        if codeowners:
                            self._printer("Code owner groups", indent=1)
                            for line, color in zip(*codeowners):
                                self._printer(line, indent=1)
                        if reviews:
                            self._section_break(indent=1)
                            self._printer("Reviews", indent=1)
                            for line in reviews:
                                self._printer(line, indent=1)
                involved_pr_table, ids = self._build_pr_table(self._involved_prs)
                codeowner_info = self._build_codeowners_tables(self._involved_prs)
                review_info = self._build_review_tables(self._involved_prs)
                if len(involved_pr_table) > 1:
                    self._section_break()
                    self._printer("WATCHING")
                    self._printer(involved_pr_table[0])
                    self._printer("Click to mute a PR", alternate=True)
                    for row, id_, codeowners, reviews in zip(
                        involved_pr_table[1:], ids, codeowner_info, review_info
                    ):
                        pull_request = self.state["pull_requests"][id_]
                        self._printer(
                            row,
                            color=self._colorize_pr(pull_request),
                            href=pull_request["browser_url"],
                        )
                        if codeowners:
                            self._printer("Code owner groups", indent=1)
                            for line, color in zip(*codeowners):
                                self._printer(line, indent=1)
                        if reviews:
                            self._section_break(indent=1)
                            self._printer("Reviews", indent=1)
                            for line in reviews:
                                self._printer(line, indent=1)
                        self._printer(
                            f"{row.rsplit(maxsplit=3)[0]}",
                            alternate=True,
                            bash="/usr/bin/curl",
                            param1='"localhost:{}/mute_pr?pr={}"'.format(
                                CONFIG["port"], pull_request["id"]
                            ),
                            refresh=True,
                        )

            self._section_break()
            self._printer("Utilities")
            if self.muted_prs:
                self._printer("Muted pull requests", indent=1)
                self._printer("Click to unmute", indent=2)
                self._section_break(indent=2)
                for pr in self.muted_prs:
                    self._printer(
                        pr["description"],
                        indent=2,
                        bash="/usr/bin/curl",
                        param1='"localhost:{}/unmute_pr?pr={}"'.format(
                            CONFIG["port"], pr["id"]
                        ),
                        refresh=True,
                    )
            self._printer(
                f"{'Enable' if not self.state['mentions_only'] else 'Disable'} mentions only mode",
                indent=1,
                bash="/usr/bin/curl",
                param1=f"localhost:{CONFIG['port']}/toggle_mentions",
                refresh=True,
            )
            self._printer(
                "Force refresh",
                indent=1,
                bash="/usr/bin/curl",
                param1=f"localhost:{CONFIG['port']}/refresh",
            )
            self._printer(
                "Kill server",
                indent=1,
                bash="kill",
                param1=str(PID),
                open_terminal=True
            )
            self._printer(
                "Open config file",
                indent=1,
                bash="$EDITOR",
                param1=CONFIG["config_file_path"],
                open_terminal=True
            )
            self._printer(f"Server PID: {PID}", indent=1)
            if self.state["last_update"]:
                update_time = datetime.strftime(
                    datetime.utcfromtimestamp(self.state["last_update"]), "%H:%M:%S"
                )
            else:
                update_time = "None"
            self._printer(f"Last update (UTC): {update_time}", indent=1)
