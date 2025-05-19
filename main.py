#!/usr/bin/env python3

import click
from cli.commands import new_command, generate_command, firebase_command

@click.group()
def cli():
    """Flutter App Creator (FAC) - Generate full-featured Flutter applications from YAML"""
    pass

cli.add_command(new_command.new)
cli.add_command(generate_command.generate)
cli.add_command(firebase_command.firebase)

if __name__ == "__main__":
    cli()