#!/usr/bin/env python3

from ahab.job_command import JobCommand
from cleo.application import Application

def cli():
    cli = Application()
    cli.add(JobCommand())
    cli.run()

if __name__ == '__main__':
    cli()