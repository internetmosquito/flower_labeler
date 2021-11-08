import os
import json
from pathlib import Path


def get_default(config_name: str, value_name: str):
    """Get default configuration values.

    Args:
        config_name (str): Name of relevant config file.
        value_name (str): Name of the key within the the
            config being loaded.

    Returns:
        The value corresponding to the requested key.

    """
    path = os.path.dirname(os.path.realpath(__file__))
    conf = str(Path(path).parents[0])
    file = os.path.join(conf, f'conf/{config_name}.json')

    with open(file, encoding='utf-8') as f:
        data = json.load(f)
    return data[value_name]
