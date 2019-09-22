from github_menubar.config import CONFIG, DEFAULT_CONFIG

import ruamel.yaml


class CorruptConfigFile(Exception):
    pass


class InvaldConfigKey(Exception):
    pass


def load_config():
    try:
        yaml = ruamel.yaml.YAML()
        return yaml.load(open(CONFIG["config_file_path"]).read())
    except FileNotFoundError:
        raise
    except Exception:
        raise CorruptConfigFile


def update_config(key, value, new=False):
    config = load_config()
    if new or key in config:
        value = value.lower()
        if value == "true":
            value = True
        elif value == "false":
            value = False
        config[key] = value
    else:
        raise InvaldConfigKey
    yaml = ruamel.yaml.YAML()
    yaml.dump(config, open(CONFIG["config_file_path"], 'w'))


def upgrade_config():
    yaml = ruamel.yaml.YAML()
    try:
        existing_config = yaml.load(open(CONFIG["config_file_path"]).read())
    except Exception:
        return
    default_config = yaml.load(DEFAULT_CONFIG)
    for key, value in existing_config.items():
        if key in default_config:
            default_config[key] = value
    yaml.dump(default_config, open(CONFIG["config_file_path"], 'w'))


