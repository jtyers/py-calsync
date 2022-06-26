import yaml


def get_config(filename):
    with open(filename, "r") as f:
        return yaml.safe_load(f)
