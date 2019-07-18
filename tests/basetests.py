"""Base tests of local borg backups."""
from logging import getLogger
import os

import yaml

from borgit.command import perform_backup
from borgit.repo import BorgRepo


def test_base():
    """Perform a basic test of local borg backup."""
    with open('tests/base.conf') as conf_handle:
        config = yaml.safe_load(conf_handle.read())
    config['backup_source_paths'] = os.path.join(
        os.path.dirname(__file__),
        config['backup_source_paths'],
    )
    repo = BorgRepo(
        repo=config['local_destination_path'],
        repo_key=config['repo_passphrase'],
        working_directory='/tmp',
    )
    repo.init()
    archive_name = 'base_test'
    logger = getLogger()
    perform_backup(repo, archive_name, config, logger)
