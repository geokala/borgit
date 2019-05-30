"""Tools for handling borgit config."""
from borgit_data import(
    validate_local_executable,
    validate_local_file_path,
    validate_remote_borg_address,
    validate_size_input,
    validate_string,
)


CONF_STRUCTURE = {
    'repo_passphrase': {
        'validate': validate_string,
        'type': 'single',
        'description': 'Passphrase for repository.',
        'optional': False,
    },
    'working_directory': {
        'validate': validate_local_file_path,
        'type': 'single',
        'description': 'Prefix for temporary files.',
        'default': '/tmp',
        'optional': True,
    },
    'local_destination_path': {
        'validate': validate_local_file_path,
        'type': 'single',
        'description': 'Local backup repository destination.',
        'optional': False,
    },
    'remote_destination_path': {
        'validate': validate_remote_borg_address,
        'type': 'single',
        'description': 'Remote backup repository destination.',
        'optional': False,
    },
    'backup_source_paths': {
        'validate': validate_local_file_path,
        'type': 'list',
        'description': 'Local directories to back up.',
        'optional': True,
    },
    'check_files': {
        'contents': {
            'path': {
                'validate': validate_local_file_path,
                'type': 'list',
                'description': 'Path to check in backup.',
                'optional': False,
            },
            'check_command': {
                'validate': validate_local_executable,
                'type': 'single',
                'description': (
                    'Script to run to check. Any output will be added to '
                    'backup notifications, as INFO if the check is '
                    'successful, WARNING if it exits with a code of 1 '
                    'or ERROR if it exits witha code of 2'
                ),
                'optional': False,
            },
            'check_arguments': {
                'validate': None,  # These could be anything, we will str them
                'type': 'list',
                'description': (
                    'Arguments to run check script with.',
                ),
                'optional': True,
            },
            'minimum_size': {
                'validate': validate_size_input,
                'type': 'single',
                'description': (
                    'Notify if the specified files are below this size. '
                    'e.g. 4M would notify if the file was smaller than 4MB.'
                ),
                'optional': True,
            },
        },
        'type': 'list_of_dicts',
        'description': (
            'Files to check and check approaches to use. '
            'These checks will be run after every backup is taken. '
            'You may need a lot of space as files to be checked will be '
            'extracted from the backup, checked, then removed (so large '
            'files may cause temporary high disk and network usage).'
        ),
        'optional': True,
    },
    'check_file_extraction_location': {
        'validate': validate_local_file_path,
        'type': 'single',
        'description': (
            'Where to store extracted backups during checking. '
            'Default is to use python secure tempdir creation.'
        ),
        'optional': True,
    },
}


def validate_config(config, prefix=None):
    """Validate the provided config, based on the defined CONF_STRUCTURE."""
    prefix = prefix or []

    configuration_issues = []
    for conf_entry, schema in CONF_STRUCTURE.items():
        key_name = '.'.join(prefix + [conf_entry])
        if conf_entry not in config:
            config[conf_entry] = schema.get('default')
            if not schema['optional']:
                configuration_issues.append(
                    '{key} was not found in configuration, but is required.'
                    .format(key=key_name)
                )
            # No need to validate an empty or default configuration entry.
            continue

        if schema['type'] == 'list_of_dicts':
            configuration_issues.extend(
                validate_config(
                    config=config[conf_entry],
                    prefix=prefix.append(conf_entry)
                )
            )

        validation = schema.get('validation')
        if validation:
            if schema['type'] == 'single':
                entry = [config[conf_entry]]
            elif schema['type'] == 'list':
                entry = config[conf_entry]
                if not isinstance(entry, list):
                    configuration_issues.append(
                        '{key} is expected to be a list but was not.'
                        .format(key=key_name)
                    )
            else:
                raise RuntimeError(
                    'Unknown type in schema: {schema_type}'.format(
                        schema_type=schema['type'],
                    )
                )
            entry_issue = validation(entry)
            if entry_issue:
                entry_issue = (
                    '{key} is invalid: {issue}'.format(
                        key=key_name,
                        issue=entry_issue,
                    )
                )
                configuration_issues.append(entry_issue)

    if prefix:
        return configuration_issues

    # We are at the top level, raise any configuration issues
    if configuration_issues:
        raise InvalidConfiguration('\n'.join(configuration_issues))
    return []


class InvalidConfiguration(Exception):
    """Raised when configuration issues are encountered in validation."""
