#!/usr/bin/env python3

from job_command import JobCommand
from cleo.application import Application

cli = Application()
cli.add(JobCommand())

if __name__ == '__main__':
    cli.run()