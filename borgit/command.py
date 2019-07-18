#! /usr/bin/env python3
"""Script for automation of borg backups, including testing the backups.
This wants to keep one local and remote copy."""
import os
import subprocess
import tempfile

from borgit.repo import BorgRepo


class CheckFailure(Exception):
    """Raised when integrity checks of a backup fail."""


def get_repos(config):
    """Get the local and remote repos to perform backup tasks.

    :param config: A valid borg config dict.

    :returns: A dict containing 'local' and 'remote' keys. The value of each
              is a BorgRepo object referring to the specified repo.
    """
    local_args = {
        'repo': config['local_destination_path'],
        'repo_key': config['repo_passphrase'],
        'working_directory': tempfile.mkdtemp(
            prefix=config['working_directory'],
        ),
    }
    remote_args = {
        'repo': config['remote_destination_path'],
        'repo_key': config['repo_passphrase'],
        'working_directory': tempfile.mkdtemp(
            prefix=config['working_directory'],
        ),
    }
    return {
        'local': BorgRepo(**local_args),
        'remote': BorgRepo(**remote_args),
    }


def pre_backup_check(repos):
    """Check the repos before the backup commences.

    :param repos: Repos obtained via a get_repos call.
    """
    for repo in 'local', 'remote':
        repos[repo].check()

        # TODO: Check the ordering of this is deterministic
        most_recent_archive = repos[repo].list_archives()[-1]
        repos[repo].check_archive(most_recent_archive)


def perform_backup(repo, archive_name, config, logger):
    """Perform a backup to the specified repo, and validate the files.

    :param repo: A BorgRepo object.
    :param config: A valid borg config dict.
    :param logger: A logger to provide file validation output.
    """
    repo.backup(archive_name, config['backup_source_paths'])

    integrity_failure = False
    for check in config['check_files']:
        check_command = [os.path.join('check_commands', check['command'])]
        check_command.extend(check['arguments'])
        check_command.append(check['path'])
        proc = subprocess.Popen(
            check_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = proc.communicate()
        for line in stdout.splitlines():
            logger.info(line)
        if proc.returncode != 0:
            logger.error('Backup integrity check failed!')
            output = logger.error
            integrity_failure = True
        else:
            output = logger.warn
        for line in stderr.splitlines():
            output(line)

    # Make sure we fail noisily if for whatever reason the archive has become
    # corrupted.
    repo.check()
    repo.check_archive(archive_name)

    if integrity_failure:
        raise CheckFailure('Backup file checks failed.')

# run_backup command:
    #   0. Validate local and remote repositories, abort if one corrupt, but not if
    # file check failed)
#   1. Do backup to local location
#   2. Validate local backup (abort if repository corrupt, but not if file check
#   failed)
# 3. Do backup to remote location
# 4. Validate remote backup
#
# Also needed:
#  - config_validate command
#  - validate_backup command
#
# For extracting files for testing, we have to remove the leading /, but
# otherwise it's just a local file path
#
# We'll need to import the config validation
