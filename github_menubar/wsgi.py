from github_menubar import GitHubClient
from github_menubar.server import app as application

if __name__ == "__main__":
    application.client = GitHubClient()
    application.run()
