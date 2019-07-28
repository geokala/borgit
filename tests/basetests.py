"""Base tests of local borg backups."""
import logging
import os
import shutil
from tempfile import mkdtemp

import pytest

from borgit.command import perform_backup
from borgit.exceptions import CheckFailure
from borgit.repo import BorgRepo


class _TestLogger:
    """Logger for use in tests, to allow checking output.
    All messages stored are also emitted to aid debugging on test failures.
    """
    def __init__(self):
        """Initialise the test logger."""
        self._logger = logging.getLogger('Testlogger')
        self._logger.setLevel(logging.DEBUG)
        self.messages = {
            'info': [],
            'warning': [],
            'error': [],
        }

    def info(self, message):
        """Store and emit an info message."""
        self.messages['info'].append(message)
        self._logger.info(message)

    def warning(self, message):
        """Store and emit a warning message."""
        self.messages['warning'].append(message)
        self._logger.warning(message)

    def error(self, message):
        """Store and emit an error message."""
        self.messages['error'].append(message)
        self._logger.error(message)

    def has_log_entry(self, words, level):
        """Check a message in the given level has specified words."""
        for message in self.messages[level]:
            if isinstance(message, bytes):
                message = message.decode('UTF-8')
            if all(word.lower() in message.lower() for word in words):
                return True
        return False


def test_local():
    """Perform a basic test of local borg backup."""
    workdir = mkdtemp(prefix='borgit-test-local-')

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
    archive_name = 'local_test'
    logger = _TestLogger()
    perform_backup(repo, archive_name, config, logger)

    shutil.rmtree(workdir)

def test_local_failed_check():
    """Perform a local test with a failed check."""
    workdir = mkdtemp(prefix='borgit-test-local-failcheck-')

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
                'arguments': ['--min-entries=200'],
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
    archive_name = 'local_failcheck_test'
    logger = _TestLogger()
    with pytest.raises(CheckFailure) as err:
        perform_backup(repo, archive_name, config, logger)
        assert 'failed' in str(err).lower()

    assert logger.has_log_entry(
        words=['backup', 'check', 'failed'],
        level='error',
    )
    assert logger.has_log_entry(
        words=['at least', '200', 'required', 'base/test.kdb'],
        level='error',
    )

    shutil.rmtree(workdir)


def test_local_no_checks():
    """Perform a basic test of local borg backup."""
    workdir = mkdtemp(prefix='borgit-test-local-')

    config = {
        'repo_passphrase': 'base_test',
        'local_destination_path': os.path.join(workdir, 'repo'),
        'remote_destination_path': None,
        'backup_source_paths': os.path.join(
            os.path.dirname(__file__),
            'base',
        ),
        'working_directory': workdir,
    }

    repo = BorgRepo(
        repo=config['local_destination_path'],
        repo_key=config['repo_passphrase'],
        working_directory=config['working_directory'],
    )
    repo.init()
    archive_name = 'local_test'
    logger = _TestLogger()
    perform_backup(repo, archive_name, config, logger)

    shutil.rmtree(workdir)
