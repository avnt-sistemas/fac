import os
import re
import yaml
import shutil
import subprocess
from jinja2 import Environment, FileSystemLoader
from utils.case_converter import CaseConverter
from utils.file_manager import FileManager
from utils.flutter_cli import FlutterCLI
from utils.dependency_manager import DependencyManager
from generators.theme_generator import ThemeGenerator
from generators.auth_generator import AuthGenerator
from generators.model_generator import ModelGenerator
from generators.firebase_generator import FirebaseGenerator
from generators.dashboard_generator import DashboardGenerator
from generators.sqlite_generator import SQLiteGenerator


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

        # Initialize Dependency Manager
        self.dependency_manager = DependencyManager(self.flutter_cli, self.config)

        # Set up Jinja2 environment
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def _load_config(self):
        """Load the YAML configuration file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
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
        print("📱 Creating base Flutter project...")
        try:
            self.flutter_cli.create_project(
                name=safe_name,
                org=package_name,
                output_dir=self.output_dir
            )
            print("✅ Base Flutter project created successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create Flutter project. Details: {e}")
            print("Make sure you have Flutter installed and that the name and organization are valid.")
            raise

        # Generate project structure
        print("🏗️ Generating project structure...")
        try:
            self._generate_project_structure(app_dir)
            print("✅ Project structure generated successfully.")
        except Exception as e:
            print(f"❌ Error generating project structure: {e}")
            raise

        # Update pubspec.yaml with custom template (for metadata and assets)
        print("📝 Updating pubspec.yaml with template...")
        try:
            self._update_pubspec_template(app_dir)
            print("✅ pubspec.yaml updated successfully.")
        except Exception as e:
            print(f"❌ Error updating pubspec.yaml: {e}")

        # Install dependencies FIRST using the new dependency manager
        print("📦 Installing dependencies...")
        try:
            self.dependency_manager.install_dependencies(app_dir)
            print("✅ Dependencies installed successfully.")
        except Exception as e:
            print(f"⚠️ Warning: Error installing dependencies: {e}")
            print("You may need to run 'flutter pub get' manually later.")

        # Generate theme
        if 'theme' in self.config:
            print("🎨 Generating theme...")
            try:
                theme_generator = ThemeGenerator(app_dir, self.config)
                theme_generator.generate()
                print("✅ Theme generated successfully.")
            except Exception as e:
                print(f"❌ Error generating theme: {e}")

        # Setup Firebase BEFORE authentication if Firebase is used
        firebase_used = (
                self.config.get('auth', {}).get('provider') == 'firebase' or
                self.config.get('persistence', {}).get('provider') == 'firebase'
        )

        if firebase_used:
            print("🔥 Setting up Firebase...")
            try:
                firebase_generator = FirebaseGenerator(app_dir, self.config, self.dependency_manager)
                firebase_generator.setup_firebase()
                print("✅ Firebase setup completed.")

                # Show Firebase configuration info
                firebase_info = firebase_generator.get_firebase_config_info()
                print(f"📋 Firebase Info:")
                print(f"  Project ID: {firebase_info['project_id']}")
                print(f"  Platforms: {', '.join(firebase_info['configured_platforms'])}")
                print(f"  firebase_options.dart: {'✅' if firebase_info['firebase_options_exists'] else '❌'}")

            except Exception as e:
                print(f"❌ Error setting up Firebase: {e}")
                print("⚠️ You may need to configure Firebase manually later.")

        # Generate authentication if enabled
        if self.config.get('auth', {}).get('enabled', False):
            print("🔐 Generating authentication...")
            try:
                auth_generator = AuthGenerator(app_dir, self.config)
                auth_generator.generate()
                print("✅ Authentication generated successfully.")
            except Exception as e:
                print(f"❌ Error generating authentication: {e}")

        # Configure persistence (SQLite or Firebase)
        persistence_provider = self.config.get('persistence', {}).get('provider', 'sqlite')

        # Generate SQLite infrastructure if SQLite is the provider
        if persistence_provider == 'sqlite':
            print("🗃️ Setting up SQLite persistence...")
            try:
                sqlite_generator = SQLiteGenerator(app_dir, self.config)
                sqlite_generator.generate()
                print("✅ SQLite persistence setup completed.")
            except Exception as e:
                print(f"❌ Error setting up SQLite persistence: {e}")

        # Generate modules
        if 'modules' in self.config:
            print("🧩 Generating modules...")
            try:
                model_generator = ModelGenerator(app_dir, self.config)
                for module_config in self.config['modules']:
                    module_name = module_config.get('name', 'Unknown')
                    print(f"📄 Generating module: {module_name}")
                    model_generator.generate_module(module_config)
                print("✅ Modules generated successfully.")
            except Exception as e:
                print(f"❌ Error generating modules: {e}")

        # Generate dashboard if enabled
        if self.config.get('dashboard', {}).get('enabled', False):
            print("📊 Generating dashboard...")
            try:
                dashboard_generator = DashboardGenerator(app_dir, self.config)
                dashboard_generator.generate()
                print("✅ Dashboard generated successfully.")
            except Exception as e:
                print(f"❌ Error generating dashboard: {e}")

        # Final pub get to ensure everything is working
        print("🔄 Running final 'flutter pub get'...")
        try:
            self.flutter_cli.pub_get(app_dir)
            print("✅ Final dependencies check completed.")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning: Failed to run final 'flutter pub get'. Details: {e}")

        print(f"\n🎉 Flutter application '{app_name}' created successfully!")
        print(f"📁 Location: {app_dir}")

        # Show dependency verification
        self._show_final_status(app_dir)

    def _show_final_status(self, app_dir: str):
        """Show final status of the generated application"""
        print(f"\n📋 Final Status Report:")

        # Check key files
        key_files = {
            'pubspec.yaml': 'Project configuration',
            'lib/main.dart': 'Main application file',
            'lib/app/app.dart': 'App widget',
            'lib/app/routes.dart': 'Route configuration',
        }

        # Add Firebase-specific files if Firebase is used
        if (self.config.get('auth', {}).get('provider') == 'firebase' or
                self.config.get('persistence', {}).get('provider') == 'firebase'):
            key_files['lib/firebase_options.dart'] = 'Firebase configuration'

        print("\n📄 Key Files:")
        for file_path, description in key_files.items():
            full_path = os.path.join(app_dir, file_path)
            status = "✅" if os.path.exists(full_path) else "❌"
            print(f"  {status} {file_path} - {description}")

        # Show dependency status
        print("\n📦 Dependencies:")
        try:
            verification = self.dependency_manager.verify_dependencies(app_dir)
            missing_deps = [dep for dep, installed in verification.items() if not installed]

            if not missing_deps:
                print("  ✅ All required dependencies are installed")
            else:
                print(f"  ❌ Missing dependencies: {', '.join(missing_deps)}")
        except Exception as e:
            print(f"  ⚠️ Could not verify dependencies: {e}")

        # Show next steps
        self._show_next_steps(app_dir)

    def _show_next_steps(self, app_dir: str):
        """Show next steps for the user"""
        app_name = os.path.basename(app_dir)

        print(f"\n🚀 Next Steps:")
        print(f"  1. cd {app_dir}")
        print(f"  2. flutter run")

        # Firebase-specific next steps
        if (self.config.get('auth', {}).get('provider') == 'firebase' or
                self.config.get('persistence', {}).get('provider') == 'firebase'):
            print(f"\n🔥 Firebase Setup:")
            print(f"  • If firebase_options.dart contains placeholders, run:")
            print(f"    flutterfire configure --project={self._get_firebase_app_id()}")
            print(f"  • Configure your Firebase project at: https://console.firebase.google.com")

        # Module-specific next steps
        if self.config.get('modules'):
            print(f"\n🧩 Generated Modules:")
            for module in self.config.get('modules', []):
                module_name = module.get('name', 'Unknown')
                print(f"  • {module_name} - CRUD operations ready")

        print(f"\n📚 Documentation:")
        print(f"  • Check generated README.md for detailed information")
        print(f"  • Review lib/app/routes.dart for available routes")

    def _get_firebase_app_id(self) -> str:
        """Get Firebase app ID from config or derive from package name"""
        if 'firebase_app' in self.config.get('app', {}):
            return self.config['app']['firebase_app']

        package_name = self.config.get('app', {}).get('package', '')
        if '.' in package_name:
            return package_name.split('.')[-1]

        app_name = self.config.get('app', {}).get('name', 'flutter-app')
        return re.sub(r'[^a-z0-9-]', '-', app_name.lower())

    def _generate_project_structure(self, app_dir):
        """Generate the base project structure"""
        # Create directories
        dirs = [
            'lib/app/theme',
            'lib/core/constants',
            'lib/core/errors',
            'lib/core/services',
            'lib/core/widgets',
            'lib/core/data/datasources',
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
            'assets/db',  # Para armazenar migrações SQL
            'lib/l10n', # Para arquivos de tradução
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

        # Generate localizations
        if self.config.get('translations', {}).get('enabled', True):
            print("🌍 Generating localizations...")
            self._generate_localizations(app_dir)

        # Generate flutter commands
        self.app_dir = app_dir

    def _generate_app_files(self, app_dir):
        """Generate the base application files"""
        try:
            # Lista de templates que queremos verificar
            templates_to_check = [
                'app/main.dart.jinja',
                'app/app.dart.jinja',
                'app/routes.dart.jinja',
                'app/dependency_injection.dart.jinja'
            ]

            # Verificar os templates usando tratamento de exceções
            for template_path in templates_to_check:
                try:
                    # Tenta obter o template - se não existir, lançará uma exceção
                    self.jinja_env.get_template(template_path)
                except Exception as e:
                    print(f"⚠️ Template '{template_path}' não encontrado: {e}")

            # Generate main.dart
            try:
                template = self.jinja_env.get_template('app/main.dart.jinja')
                output = template.render(
                    app_name=self.config['app']['name'],
                    has_auth=self.config.get('auth', {}).get('enabled', False),
                    auth_provider=self.config.get('auth', {}).get('provider', 'firebase'),
                    persistence_provider=self.config.get('persistence', {}).get('provider', 'sqlite'),
                    modules=self.config.get('modules', []),
                    firebase_enabled=(
                            self.config.get('auth', {}).get('provider') == 'firebase' or
                            self.config.get('persistence', {}).get('provider') == 'firebase'
                    )
                )

                main_dart_path = os.path.join(app_dir, 'lib', 'main.dart')
                os.makedirs(os.path.dirname(main_dart_path), exist_ok=True)
                with open(main_dart_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(output)
            except Exception as e:
                print(f"❌ Erro ao gerar main.dart: {e}")

            modules = self.config.get('modules', [])
            c = CaseConverter()

            for module in modules:
                if 'name' in module:
                    module['camel_name'] = c.to_camel_case(module['name'])
                    module['snake_name'] = c.to_snake_case(module['name'])
                    module['pascal_name'] = c.to_pascal_case(module['name'])

            # Generate app.dart
            try:
                template = self.jinja_env.get_template('app/app.dart.jinja')
                output = template.render(
                    app_name=self.config['app']['name'],
                    has_auth=self.config.get('auth', {}).get('enabled', False),
                    persistence_provider=self.config.get('persistence', {}).get('provider', 'sqlite'),
                    modules=modules,
                    firebase_enabled=(
                            self.config.get('auth', {}).get('provider') == 'firebase' or
                            self.config.get('persistence', {}).get('provider') == 'firebase'
                    )
                )

                app_dart_path = os.path.join(app_dir, 'lib', 'app', 'app.dart')
                os.makedirs(os.path.dirname(app_dart_path), exist_ok=True)
                with open(app_dart_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(output)
            except Exception as e:
                print(f"❌ Erro ao gerar app.dart: {e}")

            # Processar relacionamentos reversos com nomes únicos
            modules = []
            for m in self.config.get('modules', []):
                mc = m.copy()
                mc['snake_name'] = self.case_converter.to_snake_case(m['name'])
                modules.append(mc)

            # Generate routes.dart
            try:
                template = self.jinja_env.get_template('app/routes.dart.jinja')
                output = template.render(
                    modules=modules,
                    has_auth=self.config.get('auth', {}).get('enabled', False),
                    has_dashboard=self.config.get('dashboard', {}).get('enabled', False)
                )

                routes_dart_path = os.path.join(app_dir, 'lib', 'app', 'routes.dart')
                os.makedirs(os.path.dirname(routes_dart_path), exist_ok=True)
                with open(routes_dart_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(output)
            except Exception as e:
                print(f"❌ Erro ao gerar routes.dart: {e}")

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
                    print(f"❌ Erro ao gerar dependency_injection.dart: {e}")

        except Exception as e:
            print(f"❌ Erro ao gerar arquivos do app: {e}")
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
            print(f"❌ Error generating core widgets: {e}")
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
            print(f"❌ Error generating error handlers: {e}")
            raise

    def _update_pubspec_template(self, app_dir):
        """
        Atualiza o pubspec.yaml usando o template Jinja2 para metadados e assets.
        As dependências já foram instaladas pelo DependencyManager.
        """
        try:
            pubspec_path = os.path.join(app_dir, 'pubspec.yaml')

            # Le o pubspec atual (que já tem as dependências instaladas)
            with open(pubspec_path, 'r') as f:
                pubspec_content = f.read()


            # Aplica o template apenas para as seções que não são dependências
            template = self.jinja_env.get_template('app/pubspec.yaml.jinja')
            template_content = template.render(
                app_name=self.config['app']['name'],
                app_description=self.config['app'].get('description', 'A new Flutter project'),
                sqlite_enabled=self.config.get('persistence', {}).get('provider') == 'sqlite'
            )

            # Extrai apenas as seções flutter: e assets do template
            # e preserva as dependências que já foram instaladas
            lines = pubspec_content.split('\n')
            template_lines = template_content.split('\n')

            # Encontra onde começam as seções flutter
            flutter_section_start = -1
            for i, line in enumerate(lines):
                if line.strip().startswith('flutter:'):
                    flutter_section_start = i
                    break

            if flutter_section_start != -1:
                # Substitui a seção flutter com a do template
                new_lines = lines[:flutter_section_start]

                # Adiciona a seção flutter do template
                template_flutter_started = False
                for line in template_lines:
                    if line.strip().startswith('flutter:'):
                        template_flutter_started = True
                    if template_flutter_started:
                        new_lines.append(line)

                # Escreve o pubspec atualizado
                with open(pubspec_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write('\n'.join(new_lines))

        except Exception as e:
            print(f"❌ Error updating pubspec template: {e}")

    # Método para atualizar dependências posteriormente
    def update_dependencies(self, app_dir: str):
        """Atualiza todas as dependências para as versões mais recentes."""
        print("🔄 Updating dependencies to latest versions...")
        try:
            self.dependency_manager.update_all_dependencies(app_dir)
            print("✅ Dependencies updated successfully")
        except Exception as e:
            print(f"❌ Error updating dependencies: {e}")

    # Método para verificar status das dependências
    def check_dependencies(self, app_dir: str):
        """Verifica o status das dependências do projeto."""
        print("🔍 Checking dependency status...")
        verification = self.dependency_manager.verify_dependencies(app_dir)

        print("\n📋 Dependency Status:")
        all_good = True
        for dep, installed in verification.items():
            status = "✅" if installed else "❌"
            if not installed:
                all_good = False
            print(f"  {status} {dep}")

        if all_good:
            print("✅ All required dependencies are installed!")
        else:
            print("❌ Some dependencies are missing. Run the install command to fix.")

        return all_good

    def _generate_localizations(self, app_dir):
        """Generate .arb translation files"""
        try:
            l10n_dir = os.path.join(app_dir, 'lib', 'l10n')
            os.makedirs(l10n_dir, exist_ok=True)

            # Render en
            template = self.jinja_env.get_template('l10n/app_en.arb.jinja')
            output = template.render(
                app_name=self.config['app']['name'],
                modules=self._process_modules()
            )
            with open(os.path.join(l10n_dir, 'app_en.arb'), 'w', encoding='utf-8') as f:
                f.write(output)

            # Render pt
            template = self.jinja_env.get_template('l10n/app_pt.arb.jinja')
            output = template.render(
                app_name=self.config['app']['name'],
                modules=self._process_modules()
            )
            with open(os.path.join(l10n_dir, 'app_pt.arb'), 'w', encoding='utf-8') as f:
                f.write(output)

            self._run_flutter_genl10n(app_dir)

        except Exception as e:
            print(f"Erro ao gerar arquivos de tradução: {e}")

    def _run_flutter_genl10n(self, app_dir):
        """Run `flutter gen-l10n` to generate localization files."""
        try:
            # print("🔄 Running `flutter gen-l10n`...")
            self.flutter_cli.pub_genl10n(app_dir)
            # print("✅ `flutter gen-l10n` completed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running `flutter gen-l10n`: {e}")

    def _process_modules(self):
        """Processa módulos e campos do YAML para templates de tradução"""
        modules = []
        c = CaseConverter()

        for module_config in self.config.get('modules', []):
            module = module_config.copy()

            # Nomes do módulo
            module['snake_name'] = c.to_snake_case(module['name'])
            module['camel_name'] = c.to_camel_case(module['name'])
            module['pascal_name'] = c.to_pascal_case(module['name'])
            modules.append(module)

        return modules
