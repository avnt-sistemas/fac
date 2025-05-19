import os
from jinja2 import Environment, FileSystemLoader


class ThemeGenerator:
    def __init__(self, app_dir, config):
        self.app_dir = app_dir
        self.config = config

        # Set up Jinja2 environment
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def generate(self):
        """Generate theme files for the Flutter app"""
        print("Generating theme files...")

        # Create directory if it doesn't exist
        theme_dir = os.path.join(self.app_dir, 'lib', 'app', 'theme')
        os.makedirs(theme_dir, exist_ok=True)

        # Extract theme configuration
        theme_config = self.config.get('theme', {})
        primary_color = theme_config.get('primary_color', '#1976D2')
        secondary_color = theme_config.get('secondary_color', '#424242')
        accent_color = theme_config.get('accent_color', '#FF4081')
        font_family = theme_config.get('font_family', 'Roboto')

        # Generate app_theme.dart
        self._generate_file(
            'app/theme/app_theme.dart.jinja',
            os.path.join(theme_dir, 'app_theme.dart'),
            {
                'primary_color': primary_color,
                'secondary_color': secondary_color,
                'accent_color': accent_color,
                'font_family': font_family
            }
        )

        # Generate app_colors.dart
        self._generate_file(
            'app/theme/app_colors.dart.jinja',
            os.path.join(theme_dir, 'app_colors.dart'),
            {
                'primary_color': primary_color,
                'secondary_color': secondary_color,
                'accent_color': accent_color
            }
        )

        # Generate dimensions.dart
        self._generate_file(
            'app/theme/dimensions.dart.jinja',
            os.path.join(theme_dir, 'dimensions.dart'),
            {}
        )

        # Generate app_text_styles.dart
        self._generate_file(
            'app/theme/app_text_styles.dart.jinja',
            os.path.join(theme_dir, 'app_text_styles.dart'),
            {
                'font_family': font_family
            }
        )

        print("Theme files generated successfully.")

    def _generate_file(self, template_path, output_path, context):
        """Generate a file from a template with the given context"""
        try:
            template = self.jinja_env.get_template(template_path)
            output = template.render(**context)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

            print(f"Generated {output_path}")
        except Exception as e:
            print(f"Error generating {output_path}: {e}")