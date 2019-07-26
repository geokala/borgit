"""Base tests of local borg backups."""
from logging import getLogger
import os
import shutil
from tempfile import mkdtemp

from borgit.command import perform_backup
from borgit.repo import BorgRepo


def test_base():
    """Perform a basic test of local borg backup."""
    workdir = mkdtemp(prefix='borgit-test-base-')

    config = {
        'repo_passphrase': 'base_test',
        'local_destination_path': os.path.join(workdir, 'repo'),
        'remote_destination_path': None,
        'backup_source_paths': os.path.join(
            os.path.dirname(__file__),
            'base',
        ),
        'check_files': [
            {
                'path': os.path.join(
                    os.path.dirname(__file__),
                    'base/test.kdb',
                ),
                'command': 'check_keepass',
                'arguments': ['--min-entries=2'],
            },
        ],
        'working_directory': workdir,
    }

    repo = BorgRepo(
        repo=config['local_destination_path'],
        repo_key=config['repo_passphrase'],
        working_directory=config['working_directory'],
    )
    repo.init()
    archive_name = 'base_test'
    logger = getLogger()
    perform_backup(repo, archive_name, config, logger)

    shutil.rmtree(workdir)

# TODO: Do the other tests
