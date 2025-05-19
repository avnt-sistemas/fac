import click
from generators.firebase_generator import FirebaseGenerator


@click.group()
def firebase():
    """Firebase related commands"""
    pass


@firebase.command()
@click.option('--app-dir', default='.', help='Directory of the Flutter app')
def setup(app_dir):
    """Set up Firebase for the Flutter app"""
    click.echo("Setting up Firebase...")

    generator = FirebaseGenerator(app_dir=app_dir)
    generator.setup_firebase()

    click.echo(click.style("✅ Firebase setup completed successfully!", fg="green"))