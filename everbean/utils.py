# coding: utf-8
import sys


def parse_command_line(app, args=None):
    if args is None:
        args = sys.argv
    remaining = []
    for i in range(1, len(args)):
        # All things after the last option are command line arguments
        if not args[i].startswith("-"):
            remaining = args[i:]
            break
        if args[i] == "--":
            remaining = args[i + 1:]
            break
        arg = args[i].lstrip("-")
        name, equals, value = arg.partition("=")
        name = name.replace('-', '_').upper()
        if not name in app.config:
            raise Exception('Unrecognized command line option: %r' % name)
        # convert to bool
        if value == 'True':
            value = True
        if value == 'False':
            value = False
        app.config[name] = value

    return remaining
