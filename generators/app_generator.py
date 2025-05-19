import os
import re
import yaml
import shutil
import subprocess
from jinja2 import Environment, FileSystemLoader
from utils.case_converter import CaseConverter
from utils.file_manager import FileManager
from utils.flutter_cli import FlutterCLI
from generators.theme_generator import ThemeGenerator
from generators.auth_generator import AuthGenerator
from generators.model_generator import ModelGenerator
from generators.firebase_generator import FirebaseGenerator
from generators.dashboard_generator import DashboardGenerator
from generators.sqlite_generator import SQLiteGenerator  # Novo gerador para SQLite


class AppGenerator:
    def __init__(self, config_path, output_dir='.', flutter_path=None):
        self.config_path = config_path
        self.output_dir = output_dir
        self.config = self._load_config()
        self.case_converter = CaseConverter()
        self.file_manager = FileManager()

        # Initialize Flutter CLI with optional path
        try:
            self.flutter_cli = FlutterCLI(flutter_path)
        except FileNotFoundError as e:
            print(f"ERROR: {e}")
            print("You need to have Flutter installed and available in your PATH to use this tool.")
            print("You can download Flutter from https://flutter.dev/docs/get-started/install")
            raise

        # Set up Jinja2 environment
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def _load_config(self):
        """Load the YAML configuration file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)

            # Validate required config fields
            if 'app' not in config:
                raise ValueError("Configuration must include 'app' section")

            if 'name' not in config['app']:
                raise ValueError("App configuration must include 'name'")

            if 'package' not in config['app']:
                raise ValueError("App configuration must include 'package'")

            return config
        except yaml.YAMLError as e:
            print(f"Error parsing config file: {e}")
            raise
        except (IOError, FileNotFoundError) as e:
            print(f"Error reading config file: {e}")
            raise

    def generate(self):
        """Generate the Flutter application"""
        app_name = self.config['app']['name']
        package_name = self.config['app']['package']

        print(f"Generating Flutter app with name: {app_name}")

        # Create Flutter project using CLI
        safe_name = self.case_converter.to_snake_case(app_name)

        # Validate the name - it should not contain spaces or special characters
        if not re.match(r'^[a-z][a-z0-9_]*$', safe_name):
            print(f"Warning: '{app_name}' converted to '{safe_name}' for Flutter compatibility")
            # If still invalid, use a fallback name
            if not re.match(r'^[a-z][a-z0-9_]*$', safe_name):
                safe_name = "flutter_app"
                print(f"Using fallback name '{safe_name}' as the converted name is still invalid")

        app_dir = os.path.join(self.output_dir, safe_name)
        print(f"App directory will be: {app_dir}")

        # Create base Flutter project
        print("Creating base Flutter project...")
        try:
            self.flutter_cli.create_project(
                name=safe_name,
                org=package_name,
                output_dir=self.output_dir
            )
            print("Base Flutter project created successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to create Flutter project. Details: {e}")
            print("Make sure you have Flutter installed and that the name and organization are valid.")
            raise

        # Generate project structure
        print("Generating project structure...")
        try:
            self._generate_project_structure(app_dir)
            print("Project structure generated successfully.")
        except Exception as e:
            print(f"Error generating project structure: {e}")
            raise

        # Generate theme
        if 'theme' in self.config:
            print("Generating theme...")
            try:
                theme_generator = ThemeGenerator(app_dir, self.config)
                theme_generator.generate()
                print("Theme generated successfully.")
            except Exception as e:
                print(f"Error generating theme: {e}")

        # Generate authentication if enabled
        if self.config.get('auth', {}).get('enabled', False):
            print("Generating authentication...")
            try:
                auth_generator = AuthGenerator(app_dir, self.config)
                auth_generator.generate()
                print("Authentication generated successfully.")

                # If Firebase auth is selected, set up Firebase
                if self.config.get('auth', {}).get('provider') == 'firebase':
                    print("Setting up Firebase...")
                    firebase_generator = FirebaseGenerator(app_dir)
                    firebase_generator.setup_firebase()
                    print("Firebase setup completed.")
            except Exception as e:
                print(f"Error generating authentication: {e}")

        # Configure persistence (SQLite or Firebase)
        persistence_provider = self.config.get('persistence', {}).get('provider', 'sqlite')

        # Generate SQLite infrastructure if SQLite is the provider
        if persistence_provider == 'sqlite':
            print("Setting up SQLite persistence...")
            try:
                sqlite_generator = SQLiteGenerator(app_dir, self.config)
                sqlite_generator.generate()
                print("SQLite persistence setup completed.")
            except Exception as e:
                print(f"Error setting up SQLite persistence: {e}")

        # Generate modules
        if 'modules' in self.config:
            print("Generating modules...")
            try:
                model_generator = ModelGenerator(app_dir, self.config)  # Passou o config aqui
                for module_config in self.config['modules']:
                    print(f"Generating module: {module_config.get('name', 'Unknown')}")
                    model_generator.generate_module(module_config)
                print("Modules generated successfully.")
            except Exception as e:
                print(f"Error generating modules: {e}")

        # Generate dashboard if enabled
        if self.config.get('dashboard', {}).get('enabled', False):
            print("Generating dashboard...")
            try:
                dashboard_generator = DashboardGenerator(app_dir, self.config)
                dashboard_generator.generate()
                print("Dashboard generated successfully.")
            except Exception as e:
                print(f"Error generating dashboard: {e}")

        # Update pubspec.yaml with required dependencies
        print("Updating pubspec.yaml...")
        try:
            self._update_pubspec(app_dir)
            print("pubspec.yaml updated successfully.")
        except Exception as e:
            print(f"Error updating pubspec.yaml: {e}")

        # Run flutter pub get to install dependencies
        print("Running 'flutter pub get'...")
        try:
            self.flutter_cli.run_pub_get(app_dir)
            print("Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to run 'flutter pub get'. You may need to run it manually. Details: {e}")

        print(f"✅ Flutter application '{app_name}' created successfully at {app_dir}")

    def _generate_project_structure(self, app_dir):
        """Generate the base project structure"""
        # Create directories
        dirs = [
            'lib/app/theme',
            'lib/core/constants',
            'lib/core/errors',
            'lib/core/services',
            'lib/core/widgets',
            'lib/core/data/datasources',  # Nova pasta para persistência SQLite
            'lib/data/datasources',
            'lib/data/models',
            'lib/data/repositories',
            'lib/domain/entities',
            'lib/domain/repositories',
            'lib/domain/usecases',
            'lib/features',
            'test/core',
            'test/data',
            'test/domain',
            'test/features',
            'integration_test',
            'assets/db'  # Para armazenar migrações SQL
        ]

        for dir_path in dirs:
            full_path = os.path.join(app_dir, dir_path)
            os.makedirs(full_path, exist_ok=True)

        # Generate base files
        self._generate_app_files(app_dir)

        # Generate core widgets
        self._generate_core_widgets(app_dir)

        # Generate core error handlers
        self._generate_error_handlers(app_dir)

    def _generate_app_files(self, app_dir):
        """Generate the base application files"""
        try:
            # Lista de templates que queremos verificar
            templates_to_check = [
                'app/main.dart.jinja',
                'app/app.dart.jinja',
                'app/routes.dart.jinja',
                'app/dependency_injection.dart.jinja'  # Adicionado para SQLite
            ]

            # Verificar os templates usando tratamento de exceções
            for template_path in templates_to_check:
                try:
                    # Tenta obter o template - se não existir, lançará uma exceção
                    self.jinja_env.get_template(template_path)
                except Exception as e:
                    print(f"AVISO: O template '{template_path}' não existe ou não pode ser carregado!")
                    print(f"Erro: {e}")

            # Generate main.dart
            try:
                template = self.jinja_env.get_template('app/main.dart.jinja')
                output = template.render(
                    app_name=self.config['app']['name'],
                    has_auth=self.config.get('auth', {}).get('enabled', False),
                    auth_provider=self.config.get('auth', {}).get('provider', 'firebase'),
                    persistence_provider=self.config.get('persistence', {}).get('provider', 'sqlite'),
                    modules=self.config.get('modules', [])
                )

                main_dart_path = os.path.join(app_dir, 'lib', 'main.dart')
                os.makedirs(os.path.dirname(main_dart_path), exist_ok=True)
                with open(main_dart_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(output)
            except Exception as e:
                print(f"Erro ao gerar main.dart: {e}")

            # Generate app.dart
            try:
                template = self.jinja_env.get_template('app/app.dart.jinja')
                output = template.render(
                    app_name=self.config['app']['name'],
                    has_auth=self.config.get('auth', {}).get('enabled', False),
                    persistence_provider=self.config.get('persistence', {}).get('provider', 'sqlite'),
                    modules=self.config.get('modules', [])
                )

                app_dart_path = os.path.join(app_dir, 'lib', 'app', 'app.dart')
                os.makedirs(os.path.dirname(app_dart_path), exist_ok=True)
                with open(app_dart_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(output)
            except Exception as e:
                print(f"Erro ao gerar app.dart: {e}")

            # Generate routes.dart
            try:
                template = self.jinja_env.get_template('app/routes.dart.jinja')
                output = template.render(
                    modules=self.config.get('modules', []),
                    has_auth=self.config.get('auth', {}).get('enabled', False),
                    has_dashboard=self.config.get('dashboard', {}).get('enabled', False)
                )

                routes_dart_path = os.path.join(app_dir, 'lib', 'app', 'routes.dart')
                os.makedirs(os.path.dirname(routes_dart_path), exist_ok=True)
                with open(routes_dart_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(output)
            except Exception as e:
                print(f"Erro ao gerar routes.dart: {e}")

            # Generate dependency_injection.dart if SQLite is enabled
            if self.config.get('persistence', {}).get('provider') == 'sqlite':
                try:
                    template = self.jinja_env.get_template('app/dependency_injection.dart.jinja')
                    output = template.render(
                        app_name=self.config['app']['name'],
                        modules=self.config.get('modules', [])
                    )

                    di_path = os.path.join(app_dir, 'lib', 'app', 'dependency_injection.dart')
                    os.makedirs(os.path.dirname(di_path), exist_ok=True)
                    with open(di_path, 'w', encoding='utf-8', newline='\n') as f:
                        f.write(output)
                except Exception as e:
                    print(f"Erro ao gerar dependency_injection.dart: {e}")

        except Exception as e:
            print(f"Erro ao gerar arquivos do app: {e}")
            raise

    def _generate_core_widgets(self, app_dir):
        """Generate core widgets used in the application"""
        try:
            # Generate loading indicator
            template = self.jinja_env.get_template('core/widgets/loading_indicator.dart.jinja')
            output = template.render()

            output_path = os.path.join(app_dir, 'lib', 'core', 'widgets', 'loading_indicator.dart')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

            # Generate error message widget
            template = self.jinja_env.get_template('core/widgets/error_message.dart.jinja')
            output = template.render()

            output_path = os.path.join(app_dir, 'lib', 'core', 'widgets', 'error_message.dart')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

            # Generate empty list widget
            template = self.jinja_env.get_template('core/widgets/empty_list.dart.jinja')
            output = template.render()

            output_path = os.path.join(app_dir, 'lib', 'core', 'widgets', 'empty_list.dart')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

            # Generate confirmation dialog widget
            template = self.jinja_env.get_template('core/widgets/confirmation_dialog.dart.jinja')
            output = template.render()

            output_path = os.path.join(app_dir, 'lib', 'core', 'widgets', 'confirmation_dialog.dart')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

        except Exception as e:
            print(f"Error generating core widgets: {e}")
            raise

    def _generate_error_handlers(self, app_dir):
        """Generate error handling classes"""
        try:
            # Generate app exception class
            template = self.jinja_env.get_template('core/errors/app_exception.dart.jinja')
            output = template.render()

            output_path = os.path.join(app_dir, 'lib', 'core', 'errors', 'app_exception.dart')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

            # Generate network exception class
            template = self.jinja_env.get_template('core/errors/network_exception.dart.jinja')
            output = template.render()

            output_path = os.path.join(app_dir, 'lib', 'core', 'errors', 'network_exception.dart')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

        except Exception as e:
            print(f"Error generating error handlers: {e}")
            raise

    def _update_pubspec(self, app_dir):
        """Update pubspec.yaml with required dependencies"""
        try:
            pubspec_path = os.path.join(app_dir, 'pubspec.yaml')

            # Read existing pubspec
            with open(pubspec_path, 'r') as f:
                pubspec_content = f.read()

            # Prepare dependencies list
            dependencies = [
                "provider: ^6.0.5",  # State management
                "get_it: ^7.6.0",  # Dependency injection
                "dio: ^5.3.2",  # HTTP client
                "equatable: ^2.0.5",  # Value equality
                "shared_preferences: ^2.2.0",  # Local storage
                "intl: ^0.18.1",  # Internationalization
                "sqflite: ^2.2.8+4",  # Local database - always needed now
                "path: ^1.8.3",  # Path utilities - needed for database
                "uuid: ^4.1.0",  # Generate UUIDs for SQLite
                "path_provider: ^2.1.1",  # Access to file system directories
            ]

            # Add Firebase dependencies if using Firebase
            if (self.config.get('auth', {}).get('provider') == 'firebase' or
                    self.config.get('persistence', {}).get('provider') == 'firebase'):
                dependencies.extend([
                    "firebase_core: ^2.9.0",
                    "firebase_auth: ^4.4.0",
                    "cloud_firestore: ^4.5.0",
                ])

            # Add chart dependencies if dashboard is enabled
            if self.config.get('dashboard', {}).get('enabled', False):
                dependencies.append("fl_chart: ^0.63.0")

            # Add dependencies for exporting data if any module has exports enabled
            for module in self.config.get('modules', []):
                if module.get('export', {}).get('csv', False):
                    dependencies.append("csv: ^5.0.2")
                    break

            for module in self.config.get('modules', []):
                if module.get('export', {}).get('pdf', False):
                    dependencies.append("pdf: ^3.10.4")
                    break

            for module in self.config.get('modules', []):
                if module.get('export', {}).get('xlsx', False):
                    dependencies.append("excel: ^2.1.0")
                    break

            # Add share_plus if any export option is enabled
            if any(module.get('export', {}).get(fmt, False)
                   for module in self.config.get('modules', [])
                   for fmt in ['csv', 'pdf', 'xlsx']):
                dependencies.append("share_plus: ^7.1.0")  # Para compartilhar arquivos exportados

            # Check if dependencies section exists
            if 'dependencies:' in pubspec_content:
                # Find dependencies section and add new dependencies
                dependencies_section = pubspec_content.split('dependencies:')[1].split('\n\n')[0]

                # Add missing dependencies
                for dependency in dependencies:
                    package_name = dependency.split(':')[0].strip()
                    if package_name not in dependencies_section:
                        # Find the position to insert the new dependency
                        dependencies_end = pubspec_content.find('dependencies:') + len('dependencies:')

                        # Insert the new dependency
                        pubspec_content = pubspec_content[:dependencies_end] + f'\n  {dependency}' + pubspec_content[
                                                                                                     dependencies_end:]

            # Write updated pubspec
            with open(pubspec_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(pubspec_content)

        except Exception as e:
            print(f"Error updating pubspec.yaml: {e}")
            print("You may need to manually add the required dependencies.")