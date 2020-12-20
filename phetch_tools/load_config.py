import sys
from pathlib import Path
from typing import Dict

from yaml import BaseLoader
from yaml import load as yload


def load_config(config_file: str) -> Dict:
    config_path = Path(config_file)
    if not config_path.exists():
        print(f'Configfile {config_file} not found')
        sys.exit(1)
    config = yload(config_path.read_text(), Loader=BaseLoader)
    return config
