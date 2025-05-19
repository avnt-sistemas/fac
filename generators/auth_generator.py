import os
from jinja2 import Environment, FileSystemLoader
from utils.case_converter import CaseConverter


class AuthGenerator:
    def __init__(self, app_dir, config):
        self.app_dir = app_dir
        self.config = config
        self.case_converter = CaseConverter()

        # Set up Jinja2 environment
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def generate(self):
        """Generate authentication module for the Flutter app"""
        # Check if auth is enabled in config
        if not self.config.get('auth', {}).get('enabled', False):
            return

        # Get auth provider
        auth_provider = self.config.get('auth', {}).get('provider', 'firebase')

        # Create auth directories
        auth_dir = os.path.join(self.app_dir, 'lib', 'features', 'auth')
        os.makedirs(os.path.join(auth_dir, 'data', 'module'), exist_ok=True)
        os.makedirs(os.path.join(auth_dir, 'data', 'repositories'), exist_ok=True)
        os.makedirs(os.path.join(auth_dir, 'domain', 'entities'), exist_ok=True)
        os.makedirs(os.path.join(auth_dir, 'domain', 'repositories'), exist_ok=True)
        os.makedirs(os.path.join(auth_dir, 'presentation', 'controllers'), exist_ok=True)
        os.makedirs(os.path.join(auth_dir, 'presentation', 'screens'), exist_ok=True)
        os.makedirs(os.path.join(auth_dir, 'presentation', 'widgets'), exist_ok=True)

        # Generate user model and entity
        self._generate_user_model(auth_dir)

        # Generate auth repository
        self._generate_auth_repository(auth_dir, auth_provider)

        # Generate auth controller
        self._generate_auth_controller(auth_dir, auth_provider)

        # Generate auth screens
        self._generate_auth_screens(auth_dir, auth_provider)

        # Generate auth widgets
        self._generate_auth_widgets(auth_dir)

    def _generate_user_model(self, auth_dir):
        """Generate user model and entity"""
        # Generate user entity
        template = self.jinja_env.get_template('auth/user_entity.dart.jinja')
        output = template.render()

        output_path = os.path.join(auth_dir, 'domain', 'entities', 'user_entity.dart')
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(output)

        # Generate user model
        template = self.jinja_env.get_template('auth/user_model.dart.jinja')
        output = template.render()

        output_path = os.path.join(auth_dir, 'data', 'module', 'user_model.dart')
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(output)

    def _generate_auth_repository(self, auth_dir, auth_provider):
        """Generate auth repository interface and implementation"""
        # Generate auth repository interface
        template = self.jinja_env.get_template('auth/auth_repository_interface.dart.jinja')
        output = template.render()

        output_path = os.path.join(auth_dir, 'domain', 'repositories', 'i_auth_repository.dart')
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(output)

        # Generate auth repository implementation based on provider
        if auth_provider == 'firebase':
            template = self.jinja_env.get_template('auth/firebase_auth_repository.dart.jinja')
        else:  # local auth
            template = self.jinja_env.get_template('auth/local_auth_repository.dart.jinja')

        output = template.render()

        output_path = os.path.join(auth_dir, 'data', 'repositories', 'auth_repository_impl.dart')
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(output)

    def _generate_auth_controller(self, auth_dir, auth_provider):
        """Generate auth controller"""
        template = self.jinja_env.get_template('auth/auth_controller.dart.jinja')
        output = template.render(
            auth_provider=auth_provider
        )

        output_path = os.path.join(auth_dir, 'presentation', 'controllers', 'auth_controller.dart')
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(output)

    def _generate_auth_screens(self, auth_dir, auth_provider):
        """Generate auth screens"""
        # Generate login screen
        template = self.jinja_env.get_template('auth/login_screen.dart.jinja')
        output = template.render(
            auth_provider=auth_provider
        )

        output_path = os.path.join(auth_dir, 'presentation', 'screens', 'login_screen.dart')
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(output)

        # Generate register screen
        template = self.jinja_env.get_template('auth/register_screen.dart.jinja')
        output = template.render(
            auth_provider=auth_provider
        )

        output_path = os.path.join(auth_dir, 'presentation', 'screens', 'register_screen.dart')
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(output)

        # Generate forgot password screen
        template = self.jinja_env.get_template('auth/forgot_password_screen.dart.jinja')
        output = template.render(
            auth_provider=auth_provider
        )

        output_path = os.path.join(auth_dir, 'presentation', 'screens', 'forgot_password_screen.dart')
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(output)

        # Generate profile screen
        template = self.jinja_env.get_template('auth/profile_screen.dart.jinja')
        output = template.render()

        output_path = os.path.join(auth_dir, 'presentation', 'screens', 'profile_screen.dart')
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(output)

    def _generate_auth_widgets(self, auth_dir):
        """Generate auth widgets"""
        # Generate auth form fields
        template = self.jinja_env.get_template('auth/auth_form_fields.dart.jinja')
        output = template.render()

        output_path = os.path.join(auth_dir, 'presentation', 'widgets', 'auth_form_fields.dart')
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(output)

        # Generate social login buttons
        template = self.jinja_env.get_template('auth/social_login_buttons.dart.jinja')
        output = template.render()

        output_path = os.path.join(auth_dir, 'presentation', 'widgets', 'social_login_buttons.dart')
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(output)