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
        "arrow",
        "github3.py",
        "tabulate",
        "psutil",
        "pync",
        "apscheduler",
        "ruamel.yaml",
        "ZEO",
        "ZODB"
    ],
    entry_points={"console_scripts": ["gmb=github_menubar.github_client:main"]},
    zip_safe=False,
)
