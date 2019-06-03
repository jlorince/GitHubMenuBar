from setuptools import setup

setup(
    name='github_menubar',
    version='0.1',
    description='The funniest joke in the world',
    url='http://github.com/storborg/funniest',
    author='Jared Lorince',
    author_email='jlorince@narrativescience.com',
    license='MIT',
    packages=['github_menubar'],
    install_requites=[
        "aiohttp",
        "github3",
        "tabulate",
        "gunicorn"
    ],
    entry_points={
        'console_scripts': ['gmb-server=github_menubar.server:main'],
    },
    zip_safe=False)
