import logging
from pathlib import Path


def mute_iptcinfo_logger():
    iptcinfo_logger = logging.getLogger('iptcinfo')
    iptcinfo_logger.setLevel(logging.ERROR)


def remove_iptcinfo_backup(image_file_path):
    backup_file = Path(image_file_path + '~')
    if backup_file.exists():
        backup_file.unlink()