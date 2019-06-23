from setuptools import setup

setup(
    name="github_menubar",
    version="0.1",
    description="GitHubMenubar",
    url="https://github.com/jlorince/GitHubMenuBar",
    author="Jared Lorince",
    author_email="jlorince@narrativescience.com",
    license="MIT",
    packages=["github_menubar"],
    install_requires=[
        "github3.py",
        "tabulate",
        "psutil",
        "pync",
        "flask",
        "requests",
        "apscheduler",
        "ruamel.yaml"
    ],
    entry_points={"console_scripts": ["gmb-server=github_menubar.server:main"]},
    zip_safe=False,
)
