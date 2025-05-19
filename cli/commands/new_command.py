import click
import os
from generators.app_generator import AppGenerator


@click.command()
@click.option('--config', required=True, type=click.Path(exists=True), help='Path to the configuration YAML file')
@click.option('--output-dir', default='.', help='Directory where the Flutter app will be created')

def new(config, output_dir):
    """Create a new Flutter application based on a YAML configuration"""
    click.echo(f"Creating new Flutter application from configuration: {config}")

    # Create app generator with the config file
    generator = AppGenerator(config_path=config, output_dir=output_dir)

    # Generate the application
    generator.generate()

    click.echo(click.style(f"✅ Flutter application created successfully!", fg="green"))