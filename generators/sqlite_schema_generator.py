"""
SQLite Schema Generator for Flutter App Creator.
This script generates SQLite table creation scripts based on module definitions.
"""

import yaml
import os
import re
from jinja2 import Environment, FileSystemLoader


def snake_case(s):
    """Convert string to snake_case."""
    s = re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()
    return s


def generate_column_type(field):
    """Generate SQLite column type based on field type."""
    dart_type = field.get('type', 'String')

    if dart_type == 'String':
        return 'TEXT'
    elif dart_type == 'int':
        return 'INTEGER'
    elif dart_type == 'double':
        return 'REAL'
    elif dart_type == 'bool':
        return 'INTEGER'  # 0 or 1
    elif dart_type == 'DateTime':
        return 'TEXT'  # ISO8601 string
    elif dart_type.startswith('List'):
        return 'TEXT'  # JSON representation
    elif dart_type == 'reference':
        return 'TEXT'  # Foreign key
    else:
        return 'TEXT'  # Default to TEXT for unknown types


def generate_create_table_statement(module):
    """Generate CREATE TABLE statement for a module."""
    module_name = module['name'].lower()
    fields = module.get('fields', [])
    soft_delete = module.get('soft_delete', False)

    # Start the CREATE TABLE statement
    sql = f"CREATE TABLE {module_name} (\n"
    sql += "  id TEXT PRIMARY KEY,\n"

    # Add fields
    for field in fields:
        field_name = field['name']
        field_type = generate_column_type(field)
        required = field.get('required', False)

        # Special case for reference fields
        if field.get('type') == 'reference':
            reference = field.get('reference', '')
            field_name = f"{field_name}_id"

        sql += f"  {field_name} {field_type}"

        if required:
            sql += " NOT NULL"

        sql += ",\n"

    # Add timestamp fields
    sql += "  createdAt TEXT NOT NULL,\n"
    sql += "  updatedAt TEXT NOT NULL"

    # Add soft delete field if needed
    if soft_delete:
        sql += ",\n  deleted INTEGER DEFAULT 0"

    sql += "\n);"

    return sql


def generate_indexes(module):
    """Generate index creation statements for a module."""
    module_name = module['name'].lower()
    fields = module.get('fields', [])
    indexes = []

    for field in fields:
        if field.get('unique'):
            field_name = field['name']
            index_sql = f"CREATE UNIQUE INDEX idx_{module_name}_{field_name} ON {module_name}({field_name});"
            indexes.append(index_sql)

    return indexes


def generate_junction_tables(modules):
    """Generate junction tables for many-to-many relationships."""
    junction_tables = []

    for module in modules:
        module_name = module['name'].lower()
        fields = module.get('fields', [])

        for field in fields:
            # Check if this is a many-to-many relationship
            if field.get('type') == 'List' and field.get('itemType') == 'reference':
                reference = field.get('reference', '')
                if reference:
                    reference_name = reference.lower()
                    junction_table = f"{module_name}_{reference_name}"

                    sql = f"CREATE TABLE {junction_table} (\n"
                    sql += f"  {module_name}_id TEXT NOT NULL,\n"
                    sql += f"  {reference_name}_id TEXT NOT NULL,\n"
                    sql += "  createdAt TEXT NOT NULL,\n"
                    sql += f"  PRIMARY KEY ({module_name}_id, {reference_name}_id),\n"
                    sql += f"  FOREIGN KEY ({module_name}_id) REFERENCES {module_name}(id) ON DELETE CASCADE,\n"
                    sql += f"  FOREIGN KEY ({reference_name}_id) REFERENCES {reference_name}(id) ON DELETE CASCADE\n"
                    sql += ");"

                    junction_tables.append(sql)

    return junction_tables


def generate_sqlite_schema(config_path, output_dir):
    """Generate SQLite schema from configuration file."""
    # Load configuration
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    # Extract modules
    modules = config.get('modules', [])

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate table creation statements
    create_tables = []
    create_indexes = []

    for module in modules:
        create_tables.append(generate_create_table_statement(module))
        create_indexes.extend(generate_indexes(module))

    # Generate junction tables for many-to-many relationships
    junction_tables = generate_junction_tables(modules)

    # Write to migration file
    output_path = os.path.join(output_dir, 'sqlite_migrations.sql')
    with open(output_path, 'w') as file:
        # Write table creation statements
        file.write("-- Table creation\n")
        for statement in create_tables:
            file.write(f"{statement}\n\n")

        # Write junction tables
        if junction_tables:
            file.write("-- Junction tables for many-to-many relationships\n")
            for statement in junction_tables:
                file.write(f"{statement}\n\n")

        # Write index creation statements
        if create_indexes:
            file.write("-- Index creation\n")
            for statement in create_indexes:
                file.write(f"{statement}\n\n")

    # Generate migration manager template parameters
    template_params = {
        'app_name': config.get('app', {}).get('name', 'MyApp'),
        'modules': modules
    }

    # Create output directory for templates if it doesn't exist
    templates_dir = os.path.join(output_dir, 'templates')
    os.makedirs(templates_dir, exist_ok=True)

    # Initialize Jinja2 environment
    env = Environment(loader=FileSystemLoader('templates'))

    # Generate database initializer
    template = env.get_template('database_initializer.dart.jinja')
    output = template.render(**template_params)

    with open(os.path.join(templates_dir, 'database_initializer.dart'), 'w') as file:
        file.write(output)

    print(f"SQLite schema generated successfully in {output_dir}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate SQLite schema from configuration')
    parser.add_argument('config', help='Path to configuration YAML file')
    parser.add_argument('--output', '-o', default='output', help='Output directory')

    args = parser.parse_args()

    generate_sqlite_schema(args.config, args.output)