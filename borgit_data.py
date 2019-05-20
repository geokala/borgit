"""Tools for handling config data for borgit."""
import os
import re


# This pattern won't perfectly match IPv4/IPv6/fqdn, but should provide enough
# utility for error output without extra complexity.
REMOTE_BORG_REGEX = re.compile(
    r'^ssh://(?P<username>[a-z]+)_backups'
    r'@(?P<fqdn_or_ip>[a-zA-Z0-9.-[\]:]+)/~/repository$'
)
SIZE_REGEX = re.compile(
    r'^(?P<value>[0-9]+)(?P<unit>[A-Za-z]+)$'
)


def validate_local_file_path(config_value):
    """Validate whether the supplied value is a local file path."""
    if not os.path.exists(config_value):
        return (
            'Could not find local path: {path}'.format(path=config_value),
        )
    return ''


def validate_string(config_value):
    """Validate that the provided value is a string."""
    if not isinstance(config_value, str):
        return (
            'Expected a string.',
        )
    return ''


def validate_remote_borg_address(config_value):
    """Validate that the value is a supported remote borg address."""
    if not REMOTE_BORG_REGEX.findall(config_value):
        return (
            'Expected remote borg backup location in the form: '
            'ssh://<username>_backups@<FQDN_OR_IP>/~/repository',
        )
    return ''


def validate_local_executable(config_value):
    """Validate that a local executable file has been provided."""
    if not os.path.isfile(config_value):
        return '{path} does not exist.'.format(path=config_value)
    if not os.access(config_value, os.X_OK):
        return '{path} is not executable.'.format(path=config_value)
    return ''


def validate_size_input(config_value):
    """Validate that a parseable size has been provided."""
    try:
        convert_size_input(config_value)
        return ''
    except SizeConversionError as err:
        return str(err)


class SizeConversionError(Exception):
    """Raised when failing an attempt to convert a size input."""


def convert_size_input(size_input):
    """Convert a size input to the appropriate size in bytes."""
    # Supported size specifiers, with the required multiplier
    supported_size_specifiers = {
        'b': 1,
        'mib': 1024,
        'mb': 1000,
        'm': 1000,
    }
    output_specifiers = ', '.join(('B', 'MiB', 'MB', 'M'))

    first_parse = SIZE_REGEX.match(size_input)
    if not first_parse:
        raise SizeConversionError(
            'Could not convert {inp} to size. Expected numbers followed by '
            'a unit ({units}). e.g. 14MiB'.format(
                inp=size_input,
                units=output_specifiers,
            )
        )

    first_parse = first_parse.groupdict()
    multiplier = supported_size_specifiers.get(first_parse['unit'].lower())
    if not multiplier:
        raise SizeConversionError(
            'Could not convert {inp} to size. Unrecognised unit {unit}. '
            'Valid units are: {units}'.format(
                inp=size_input,
                unit=first_parse['unit'],
                units=output_specifiers,
            )
        )

    return int(first_parse['value']) * multiplier
