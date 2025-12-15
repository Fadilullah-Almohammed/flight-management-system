#!/usr/bin/env python
"""Django's command-line utility for administrative tasks.

This module serves as the primary entry point for interacting with the Django
project from the command line. It handles setting up the environment and
executing management commands such as starting the server, running migrations,
and creating superusers.
"""
import os
import sys


def main():
    """Sets up the Django environment and runs command-line administrative tasks.

    This function configures the `DJANGO_SETTINGS_MODULE` environment variable
    to point to the project's settings and then delegates execution to Django's
    `execute_from_command_line` utility.

    Raises:
        ImportError: If Django cannot be imported, likely due to a missing
            installation or an inactive virtual environment.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flightsystem.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
