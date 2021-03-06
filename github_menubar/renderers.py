import sys
from datetime import datetime

from tabulate import tabulate

from github_menubar.config import COLORS, CONFIG, GLYPHS, TREX
from github_menubar.github_client import GitHubClient
from github_menubar.utils import load_config

REVIEW_STATE_MAP = {
    "COMMENTED": "comment",
    "APPROVED": "success",
    "CHANGES_REQUESTED": "error",
    "DISMISSED": "x",
    "PENDING": "in_progress",
}
TEST_STATUS_MAP = {
    "pending": "in_progress",
    "success": "success",
    "failure": "error",
    "cancelled": "cancelled",
    "neutral": "in_progress",
    "in_progress": "in_progress",
}
MERGE_STATE_COLOR_MAP = {
    "behind": "orange",
    "blocked": "orange",
    "clean": "green",
    "dirty": "red",
    "draft": "orange",
    "has_hooks": "green",
    "unknown": "orange",
    "unstable": "green",
}

MAX_LENGTH = 100
MAX_PR_LENGTH = 60


def chunkstring(string, length):
    return (string[0 + i : length + i] for i in range(0, len(string), length))


class Renderer:
    """Base class for renderers

    Implements generic renderer functionality.
    """

    def __init__(self):
        self.CONFIG = load_config()
        self.PID = open(CONFIG["pid_file"]).read().strip()
        self._client = GitHubClient()
        self.state = self._get_state()
        self.muted_prs = self._get_muted_prs()
        self.error = False

    def _get_state(self):
        state = self._client.get_state()
        return state

    def _get_muted_prs(self):
        return self._client.get_muted_prs()

    def transform_pr_url(self, api_url):
        return api_url.replace("api.github.com/repos", "github.com").replace(
            "/pulls/", "/pull/"
        )

    @property
    def _user_prs(self):
        return [
            pull_request
            for pull_request in self.state["pull_requests"].values()
            if pull_request["author"] == self.CONFIG["user"]
            and pull_request["state"] not in ("CLOSED", "MERGED")
        ]

    @property
    def _involved_prs(self):
        return [
            pull_request
            for pull_request in self.state["pull_requests"].values()
            if (
                pull_request["author"] != self.CONFIG["user"]
                and pull_request["state"] not in ("CLOSED", "MERGED")
            )
        ]

    @property
    def _pr_urls(self):
        return {pr["url"]: pr for pr in self.state["pull_requests"].values()}


class BitBarRenderer(Renderer):
    def _format(self, pr):
        text = self.CONFIG["format_string_v2"].format(**pr)
        if len(text) > MAX_PR_LENGTH:
            return f"{text[:MAX_PR_LENGTH]}..."
        return text

    def _build_notification_pr_table(self):
        rows = []
        ids = []
        notif_ids = []
        for notif_id, notification in self.state["notifications"].items():
            pr = self._pr_urls.get(notification["url"])
            if pr:
                desc = self._format(pr)
                rows.append([desc, pr["author"], pr["state"]])
                ids.append(pr["id"])
                notif_ids.append(notif_id)
        return (
            tabulate(rows, headers=["PR", "author", "state"], tablefmt="plain").split(
                "\n"
            ),
            ids,
            notif_ids,
        )

    def _colorize_pr(self, pull_request):
        if pull_request["state"] == "CLOSED":
            color = "gray"
        elif (
            pull_request["test_status"].get("outcome") == "failure"
            or pull_request["mergeable"] is False
        ):
            color = COLORS["red"]
        else:
            color = MERGE_STATE_COLOR_MAP[pull_request["mergeable_state"]]

        return color

    def _build_pr_table(self, prs):
        rows = []
        ids = []
        for pull_request in prs:
            merge_conflict = (
                GLYPHS["success"] if pull_request["mergeable"] else GLYPHS["error"]
            )
            if pull_request["protected"]:
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
            else:
                approved = GLYPHS["na"]

            test_status = (
                GLYPHS["na"]
                if pull_request["test_status"].get("outcome") is None
                else GLYPHS[TEST_STATUS_MAP[pull_request["test_status"]["outcome"]]]
            )
            rows.append(
                [
                    self._format(pull_request),
                    pull_request["mergeable_state"],
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
                    "status",
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
            if rows:
                result.append(tabulate(rows, tablefmt="plain").split("\n"))
            else:
                result.append(None)
        return result

    def _get_header_info(self):
        n_notifications = len(
            [
                notif
                for notif in self.state["notifications"].values()
                if notif["url"] in self._pr_urls
            ]
        )
        n_failing_tests = 0
        n_open_prs = 0
        n_merge_conflicts = 0
        n_ready = 0
        for pr in self.state["pull_requests"].values():
            if pr["author"] == self.CONFIG["user"]:
                n_open_prs += 1
                if pr["test_status"] and pr["test_status"].get("outcome") == "failure":
                    n_failing_tests += 1
                if pr["mergeable_state"] == "dirty":
                    n_merge_conflicts += 1
                if pr["mergeable_state"] in ("clean", "unstable"):
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
        if self.CONFIG["collapsed"]:
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
        font=None,
        color=None,
        href=None,
        refresh=False,
        alternate=False,
        bash=None,
        param1=None,
        param2=None,
        param3=None,
        open_terminal=False,
    ):
        font = font or self.CONFIG["font"]
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
            if param1 is not None:
                result += f" param1={param1}"
            if param2 is not None:
                result += f" param2={param2}"
            if param3 is not None:
                result += f" param3={param3}"
            print(result)

    def _section_break(self, indent=0):
        print(f"{'--' * indent}---")

    def _pr_section(self, pull_requests, name):
        pr_table, ids = self._build_pr_table(pull_requests)
        codeowner_info = self._build_codeowners_tables(pull_requests)
        review_info = self._build_review_tables(pull_requests)
        self._section_break()
        self._printer(name)
        self._printer(pr_table[0])
        self._printer("Click to copy URL", alternate=True)
        for row, id_, codeowners, reviews in zip(
            pr_table[1:], ids, codeowner_info, review_info
        ):
            pull_request = self.state["pull_requests"][id_]
            self._printer(
                row,
                color=self._colorize_pr(pull_request),
                href=pull_request["browser_url"],
            )
            self._printer(f"Organization: {pull_request['org']}", indent=1)
            self._printer(f"Repository: {pull_request['repo']}", indent=1)
            self._printer(f"Title: {pull_request['title']}", indent=1)
            self._printer(f"Number: {pull_request['number']}", indent=1)
            self._printer(f"Base: {pull_request['base']}", indent=1)
            self._printer(
                f"Updated: {pull_request['updated_at'].to('local').format(CONFIG['date_format'])}",
                indent=1,
            )
            self._section_break(indent=1)
            self._printer(
                f"Mute PR",
                bash=self._get_gmb(),
                param1="mute",
                param2=pull_request["id"],
                refresh=True,
                indent=1,
            )
            self._printer(
                "Copy branch name",
                bash="/bin/bash",
                param1="-c",
                param2="'printf {} | pbcopy'".format(pull_request["head"]),
                indent=1,
            )
            if codeowners:
                self._section_break(indent=1)
                self._printer("Code owner groups", indent=1)
                for line, color in zip(*codeowners):
                    self._printer(line, indent=1)
            if reviews:
                self._section_break(indent=1)
                self._printer("Reviews", indent=1)
                for line in reviews:
                    self._printer(line, indent=1)
            if pull_request["test_status"].get("runs"):
                self._section_break(indent=1)
                self._printer("Checks", indent=1)
                for check, (outcome, required) in pull_request["test_status"][
                    "runs"
                ].items():
                    self._printer(
                        f"{'*' if required else ''}{check}: {outcome}", indent=1
                    )

            self._printer(
                f"{row.rsplit(maxsplit=3)[0]}",
                alternate=True,
                bash="/bin/bash",
                param1="-c",
                param2="'printf {} | pbcopy'".format(pull_request["browser_url"]),
            )

    def _get_gmb(self):
        return f"{sys.executable.rsplit('/', 1)[0]}/gmb"

    def print_state(self):
        if self.error:
            self._printer(GLYPHS["github_logo"])
            self._section_break()
            self._printer("No connection")
        else:
            header_info = self._get_header_info()
            header = self._build_header(**header_info)
            self._printer(header, font=self.CONFIG["font_large"])
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
                    self._printer(
                        f"Dismiss all notifications",
                        bash=self._get_gmb(),
                        param1="clearall",
                        refresh=True,
                        indent=1,
                    )
                    self._printer(notif_pr_table[0])
                    self._printer("Click to copy URL", alternate=True)
                    for row, pr_id, notif_id in zip(
                        notif_pr_table[1:], pr_ids, notif_ids
                    ):
                        url = self.state["pull_requests"][pr_id]["browser_url"]
                        self._printer(
                            row,
                            bash=self._get_gmb(),
                            param1="open",
                            param2=notif_id,
                            refresh=True,
                        )
                        self._printer(
                            self.state["pull_requests"][pr_id]["description"], indent=1
                        )
                        self._printer(
                            self.state["notifications"][notif_id]["updated_at"]
                            .to("local")
                            .format(CONFIG["date_format"]),
                            indent=1,
                        )
                        self._printer(
                            f"Reason: {self.state['notifications'][notif_id]['reason']}",
                            indent=1,
                        )
                        self._section_break(indent=1)
                        self._printer(
                            f"Dismiss",
                            bash=self._get_gmb(),
                            param1="clear",
                            param2=notif_id,
                            refresh=True,
                            indent=1,
                        )
                        self._section_break(indent=1)
                        comment = self.state["notifications"][notif_id].get(
                            "comment", {}
                        )
                        if comment.get("body_text"):
                            self._printer(
                                f"Latest comment ({comment['user']['login']}):",
                                indent=1,
                            )
                            self._printer(
                                comment["body_text"].replace("\n", ""), indent=1
                            )
                        self._printer(
                            f"{row.rsplit(maxsplit=2)[0]}",
                            alternate=True,
                            bash="/bin/bash",
                            param1="-c",
                            param2="'printf {} | pbcopy'".format(url),
                        )

                if self._user_prs:
                    self._pr_section(self._user_prs, "MY PULL REQUESTS")

                if self._involved_prs:
                    self._pr_section(self._involved_prs, "WATCHING")

            self._section_break()
            self._printer("Options")
            self._printer(
                f"{GLYPHS['success'] if self.CONFIG['mentions_only'] else GLYPHS['in_progress']} Mentions only mode",
                indent=1,
                bash=self._get_gmb(),
                param1="config",
                param2="mentions_only",
                param3=not self.CONFIG["mentions_only"],
                refresh=True,
            )
            if self.CONFIG["mentions_only"]:
                self._printer(
                    f"{GLYPHS['success'] if self.CONFIG['team_mentions'] else GLYPHS['in_progress']} Team mentions",
                    indent=1,
                    bash=self._get_gmb(),
                    param1="config",
                    param2="team_mentions",
                    param3=not self.CONFIG["team_mentions"],
                    refresh=True,
                )
            self._printer(
                f"{GLYPHS['success'] if self.CONFIG['collapsed'] else GLYPHS['in_progress']} Collapse MenuBar icons",
                indent=1,
                bash=self._get_gmb(),
                param1="config",
                param2="collapsed",
                param3=not self.CONFIG["collapsed"],
                refresh=True,
            )
            self._printer(
                f"{GLYPHS['success'] if self.CONFIG['desktop_notifications'] else GLYPHS['in_progress']} Desktop notifications",
                indent=1,
                bash=self._get_gmb(),
                param1="config",
                param2="desktop_notifications",
                param3=not self.CONFIG["desktop_notifications"],
                refresh=True,
            )
            self._printer(
                f"{GLYPHS['success'] if self.CONFIG['launch_on_startup'] else GLYPHS['in_progress']} Launch on login",
                indent=1,
                bash=self._get_gmb(),
                param1="config",
                param2="launch_on_startup",
                param3=not self.CONFIG["launch_on_startup"],
                refresh=True,
            )
            self._section_break(indent=1)
            self._printer(
                "Open config file",
                indent=1,
                bash="nano",
                param1=CONFIG["config_file_path"],
                open_terminal=True,
            )

            self._printer("Utilities")
            if self.muted_prs:
                self._printer("Muted pull requests", indent=1)
                self._printer("Click to unmute", indent=2)
                self._section_break(indent=2)
                for pr in self.muted_prs:
                    self._printer(
                        pr["description"],
                        indent=2,
                        bash=self._get_gmb(),
                        param1="unmute",
                        param2=pr["id"],
                        refresh=True,
                    )
            self._printer("Icon key", indent=1)
            self._printer("PR attributes", indent=2)
            self._printer(f"{GLYPHS['merged_pr']}: Merge conflict status", indent=2)
            self._printer(f"{GLYPHS['tests']}: Test status", indent=2)
            self._printer(f"{GLYPHS['approval']}: Review status", indent=2)
            self._section_break(indent=2)
            self._printer("Status icons", indent=2)
            self._printer(
                f"{GLYPHS['success']}: OK  {GLYPHS['error']}: ERROR", indent=2
            )
            self._printer(
                f"{GLYPHS['na']}: NA  {GLYPHS['in_progress']}: PENDING", indent=2
            )
            self._printer(f"{GLYPHS['cancelled']}: CANCELLED", indent=2)
            self._printer(
                "Force refresh", indent=1, bash=self._get_gmb(), param1="refresh"
            )
            self._printer(
                "Kill server",
                indent=1,
                bash="/bin/bash",
                param1="-c",
                param2="'launchctl unload {}'".format(CONFIG['plist_path']),
                open_terminal=False,
            )
            self._section_break(indent=1)
            self._printer(f"Server PID: {self.PID}", indent=1)
            if self.state["last_update"]:
                update_time = self.state["last_update"].to("local").format(CONFIG["date_format"])
            else:
                update_time = "None"
            self._printer(f"Last update: {update_time}", indent=1)
