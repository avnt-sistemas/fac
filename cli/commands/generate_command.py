import click
from generators.model_generator import ModelGenerator


@click.group()
def generate():
    """Generate components for an existing Flutter app"""
    pass


@generate.command()
@click.option('--name', required=True, help='Name of the module to generate')
@click.option('--fields', required=True, help='Comma-separated list of field:type pairs (e.g., "name:String,age:int")')
@click.option('--app-dir', default='.', help='Directory of the Flutter app')
def module(name, fields, app_dir):
    """Generate a new module with the specified fields"""
    click.echo(f"Generating module '{name}' with fields: {fields}")

    # Parse fields
    field_list = []
    for field_str in fields.split(','):
        field_name, field_type = field_str.strip().split(':')
        field_list.append({
            'name': field_name,
            'type': field_type,
            'required': True  # Default to required
        })

    # Create module configuration
    module_config = {
        'name': name,
        'fields': field_list,
        'soft_delete': True,
        'export': {
            'csv': True,
            'xlsx': True,
            'pdf': True
        }
    }

    # Generate module and screens
    generator = ModelGenerator(app_dir=app_dir)
    generator.generate_module(module_config)

    click.echo(click.style(f"✅ Module '{name}' generated successfully!", fg="green"))