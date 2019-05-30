#! /usr/bin/env python3
"""Borgit repo handler."""
import os
import subprocess


class BorgRepo:
    """Class for working with a specific borg repository."""
    def __init__(self, repo, repo_key, working_directory):
        """Initialise borg repository handler.
        This will not actually initialise the borg repository."""
        self.repo = repo
        self.repo_key = repo_key
        self.working_directory = working_directory

    def _run_borg_command(self, command, archive_name=None, args=None):
        """Run a borg command on an archive with any (list of) args."""
        borg_env = os.environ.copy()
        borg_env.update({
            'BORG_REPO': self.repo,
            # This'll be accessible via /proc to root or anyone who can run as
            # this user... but that's true of the config file anyway.
            'BORG_PASSPHRASE': self.repo_key,
        })

        borg_command = ['borg', command]
        if archive_name:
            borg_command.append('::' + archive_name)
        if args:
            borg_command.extend(args)
        return subprocess.check_output(borg_command, env=borg_env,
                                       cwd=self.working_directory)

    def backup(self, archive_name, sources):
        """Backup data using borg."""
        self._run_borg_command(
            'create', archive_name,
            args=[
                '--stats', '--verbose', '--show-rc',
                '--compression', 'lz4',
            ] + sources,
        )

    def list_archives(self):
        """Get a list of all archives in the repository."""
        return self._run_borg_command(
            'list',
            args=['--format', '{archive}{NL}'],
        ).split(r'\n')

    def list_files_in_archive(self, archive_name):
        """Get a list of all files in an archive."""
        return self._run_borg_command(
            'list', archive_name,
            args=['--format', '{path}{NL}'],
        ).split(r'\n')

    def restore_file_from_archive(self, archive_name, path):
        """Restore specific file or directory from an archive."""
        # Paths don't have a leading / in the repository, so we'll remove any
        # supplied leading slashes.
        path = path.lstrip('/')
        self._run_borg_command(
            'extract', archive_name,
            args=[path],
        )

    def check(self):
        """Verify the integrity of the repository."""
        self._run_borg_command(
            'check',
        )

    def check_archive(self, archive_name):
        """Verify the integrity of a specific archive."""
        self._run_borg_command(
            'check', archive_name,
        )
