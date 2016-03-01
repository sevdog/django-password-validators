#!/usr/bin/env python
import os
from os.path import join, realpath, dirname
import sys


__dir__ = realpath(dirname(__file__))
sys.path.insert(0, realpath(join(__dir__, '..')))


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
