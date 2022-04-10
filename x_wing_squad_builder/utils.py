import json
import re
from _ctypes import PyObj_FromPtr
import argparse

from typing import List


def prettify_name(name: str) -> str:
    """Takes a lowercase string of a name and capitalizes it."""
    return ' '.join([part.capitalize()for part in name.split()])

def prettify_definition_form_entry(values: str) -> List[str]:
    """Takes a list of values separated by a comma, and returns a list of the values
    in lowercase with white space stripped from each side.

    :param values: string of values from the definition form
    :type values: str
    :return: list of values cleaned up.
    :rtype: List[str]
    """
    val_split = values.split(',')
    return [val.lower().strip() for val in val_split]


def create_log_level_parser():
    class NoAction(argparse.Action):
        def __init__(self, **kwargs):
            kwargs.setdefault('nargs', 0)
            super(NoAction, self).__init__(**kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            pass
    choices = {
        'debug': 'Detailed information, typically of interest only when diagnosing problems.',
        'info': 'Confirmation that things are working as expected.',
        'warning': 'An indication that something unexpected happened.  The software is still working as expected.',
        'error': 'Due to a more serious problem, the software has not been able to perform some function.',
        'critical': 'A serious error, indicating that the program itself may be unable to continue running.'
    }
    parser = argparse.ArgumentParser()
    parser.register('action', 'none', NoAction)
    parser.add_argument(
        '-log',
        '--log',
        choices=list(choices.keys()),
        default='info',
        help=(
            'Provide logging level. \n'
            'Example: --log debug \n'
        )
    )
    group = parser.add_argument_group(title='valid log level options')
    for key, value in choices.items():
        group.add_argument(key, help=value, action='none')

    return parser

class NoIndent(object):
    """ Value wrapper. """

    def __init__(self, value):
        if not isinstance(value, (list, tuple)):
            raise TypeError('Only lists and tuples can be wrapped')
        self.value = value


class PrettyJSONEncoder(json.JSONEncoder):
    FORMAT_SPEC = '@@{}@@'  # Unique string pattern of NoIndent object ids.
    regex = re.compile(FORMAT_SPEC.format(r'(\d+)'))  # compile(r'@@(\d+)@@')

    def __init__(self, **kwargs):
        # Keyword arguments to ignore when encoding NoIndent wrapped values.
        ignore = {'cls', 'indent'}

        # Save copy of any keyword argument values needed for use here.
        self._kwargs = {k: v for k, v in kwargs.items() if k not in ignore}
        super(PrettyJSONEncoder, self).__init__(**kwargs)

    def default(self, obj):
        return (self.FORMAT_SPEC.format(id(obj)) if isinstance(obj, NoIndent)
                else super(PrettyJSONEncoder, self).default(obj))

    def iterencode(self, obj, **kwargs):
        format_spec = self.FORMAT_SPEC  # Local var to expedite access.

        # Replace any marked-up NoIndent wrapped values in the JSON repr
        # with the json.dumps() of the corresponding wrapped Python object.
        for encoded in super(PrettyJSONEncoder, self).iterencode(obj, **kwargs):
            match = self.regex.search(encoded)
            if match:
                id = int(match.group(1))
                no_indent = PyObj_FromPtr(id)
                json_repr = json.dumps(no_indent.value, **self._kwargs)
                # Replace the matched id string with json formatted representation
                # of the corresponding Python object.
                encoded = encoded.replace(
                    '"{}"'.format(format_spec.format(id)), json_repr)

            yield encoded
