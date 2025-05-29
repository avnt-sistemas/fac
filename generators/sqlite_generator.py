import os
import yaml
from jinja2 import Environment, FileSystemLoader
from utils.case_converter import CaseConverter


class SQLiteGenerator:
    def __init__(self, app_dir, config):
        self.app_dir = app_dir
        self.config = config
        self.case_converter = CaseConverter()

        # Set up Jinja2 environment
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def generate(self):
        """Generate SQLite infrastructure for the Flutter app"""
        # Verify that SQLite is the persistence provider
        if self.config.get('persistence', {}).get('provider') != 'sqlite':
            return

        print("🧩 Generating SQLite infrastructure...")

        # Create directories for SQLite files
        core_datasources_dir = os.path.join(self.app_dir, 'lib', 'core', 'data', 'datasources')
        os.makedirs(core_datasources_dir, exist_ok=True)

        # Generate core SQLite services
        self._generate_sqlite_service(core_datasources_dir)
        self._generate_sqlite_helper(core_datasources_dir)
        self._generate_sqlite_relationship_helper(core_datasources_dir)
        self._generate_sqlite_schema(core_datasources_dir)
        self._generate_sqlite_migration_manager(core_datasources_dir)

        # Generate database initializer
        self._generate_database_initializer()

        # Generate export service if any module has export enabled
        if self._has_export_enabled():
            self._generate_export_service(core_datasources_dir)

        # Generate SQL migration file
        self._generate_sqlite_migrations()

    def _generate_sqlite_service(self, output_dir):
        """Generate SQLite service class"""
        try:
            template = self.jinja_env.get_template('core/data/datasources/sqlite_service.dart.jinja')
            output = template.render(
                app_name=self.config['app']['name'],
                modules=self.config.get('modules', [])
            )

            output_path = os.path.join(output_dir, 'sqlite_service.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)
        except Exception as e:
            print(f"Error generating SQLite service: {e}")

    def _generate_sqlite_helper(self, output_dir):
        """Generate SQLite helper class"""
        try:
            template = self.jinja_env.get_template('core/data/datasources/sqlite_helper.dart.jinja')
            output = template.render()

            output_path = os.path.join(output_dir, 'sqlite_helper.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)
        except Exception as e:
            print(f"Error generating SQLite helper: {e}")

    def _generate_sqlite_relationship_helper(self, output_dir):
        """Generate SQLite relationship helper class"""
        try:
            template = self.jinja_env.get_template('core/data/datasources/sqlite_relationship_helper.dart.jinja')
            output = template.render()

            output_path = os.path.join(output_dir, 'sqlite_relationship_helper.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)
        except Exception as e:
            print(f"Error generating SQLite relationship helper: {e}")

    def _generate_sqlite_schema(self, output_dir):
        """Generate SQLite schema utility class"""
        try:
            template = self.jinja_env.get_template('core/data/datasources/sqlite_schema.dart.jinja')
            output = template.render()

            output_path = os.path.join(output_dir, 'sqlite_schema.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)
        except Exception as e:
            print(f"Error generating SQLite schema utility: {e}")

    def _generate_sqlite_migration_manager(self, output_dir):
        """Generate SQLite migration manager class"""
        try:
            template = self.jinja_env.get_template('core/data/datasources/sqlite_migration_manager.dart.jinja')
            output = template.render(
                app_name=self.config['app']['name'],
                modules=self.config.get('modules', [])
            )

            output_path = os.path.join(output_dir, 'sqlite_migration_manager.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)
        except Exception as e:
            print(f"Error generating SQLite migration manager: {e}")

    def _generate_database_initializer(self):
        """Generate database initializer class"""
        try:
            output_dir = os.path.join(self.app_dir, 'lib', 'app')
            os.makedirs(output_dir, exist_ok=True)

            template = self.jinja_env.get_template('app/database_initializer.dart.jinja')
            output = template.render(
                app_name=self.config['app']['name'],
                modules=self.config.get('modules', [])
            )

            output_path = os.path.join(output_dir, 'database_initializer.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)
        except Exception as e:
            print(f"Error generating database initializer: {e}")

    def _generate_export_service(self, output_dir):
        """Generate export service class for data export functionality"""
        try:
            template = self.jinja_env.get_template('core/data/datasources/export_service.dart.jinja')
            output = template.render()

            output_path = os.path.join(output_dir, 'export_service.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)
        except Exception as e:
            print(f"Error generating export service: {e}")

    def _generate_sqlite_migrations(self):
        """Generate SQLite migrations file"""
        try:
            output_dir = os.path.join(self.app_dir, 'assets', 'db')
            os.makedirs(output_dir, exist_ok=True)

            # Import the SQLite schema generator
            from generators.sqlite_schema_generator import generate_create_table_statement, generate_indexes, \
                generate_junction_tables

            modules = self.config.get('modules', [])

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
            with open(output_path, 'w', encoding='utf-8', newline='\n') as file:
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
        except Exception as e:
            print(f"Error generating SQLite migrations file: {e}")

    def _has_export_enabled(self):
        """Check if any module has export functionality enabled"""
        for module in self.config.get('modules', []):
            if isinstance(module.get('export'), dict) and any(
                    module['export'].get(fmt, False) for fmt in ['csv', 'xlsx', 'pdf']):
                return True
            if module.get('export') is True:
                return True
        return False

    def generate_repository_impl(self, module_config, output_dir, relationships):
        """Generate repository implementation with SQLite support for a module"""
        try:
            module_name = module_config['name']
            pascal_case = self.case_converter.to_pascal_case(module_name)
            snake_case = self.case_converter.to_snake_case(module_name)

            template = self.jinja_env.get_template('module/repository_impl.dart.jinja')
            output = template.render(
                module_name=snake_case,
                pascal_case=pascal_case,
                fields=module_config.get('fields', []),
                soft_delete=module_config.get('soft_delete', False),
                relationships=relationships
            )

            output_path = os.path.join(output_dir, f'{snake_case}_repository_impl.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)
        except Exception as e:
            print(f"Error generating SQLite repository implementation for {module_config.get('name', 'unknown')}: {e}")

    def generate_list_screen_with_export(self, module_config, output_dir):
        """Generate list screen with export functionality for a module"""
        if not self._has_module_export_enabled(module_config):
            return False

        try:
            module_name = module_config['name']
            pascal_case = self.case_converter.to_pascal_case(module_name)
            snake_case = self.case_converter.to_snake_case(module_name)

            # Passo 1: Primeiro, certifique-se de que as telas de formulário e detalhe existam
            self._ensure_form_and_detail_screens(module_config, output_dir)

            # Passo 2: Agora gere a tela de listagem com exportação
            template = self.jinja_env.get_template('screens/list_screen_with_export.dart.jinja')
            output = template.render(
                entity_name=pascal_case,
                snake_case_name=snake_case,
                fields=module_config.get('fields', []),
                export=module_config.get('export', {})
            )

            output_path = os.path.join(output_dir, f'{snake_case}_list_screen.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)
            return True
        except Exception as e:
            print(f"Error generating list screen with export for {module_config.get('name', 'unknown')}: {e}")
            return False

    def _ensure_form_and_detail_screens(self, module_config, output_dir):
        """Certifique-se de que as telas de formulário e detalhe existam antes de gerar a tela de listagem"""
        module_name = module_config['name']
        pascal_case = self.case_converter.to_pascal_case(module_name)
        snake_case = self.case_converter.to_snake_case(module_name)

        # Verifique se a tela de detalhe já existe, caso contrário gere um stub
        detail_screen_path = os.path.join(output_dir, f'{snake_case}_detail_screen.dart')
        if not os.path.exists(detail_screen_path):
            try:
                template = self.jinja_env.get_template('screens/detail_screen.dart.jinja')
                output = template.render(
                    module_name=module_name,
                    pascal_case=pascal_case,
                    snake_case_name=snake_case,
                    entity_name=pascal_case,
                    fields=module_config.get('fields', []),
                    soft_delete=module_config.get('soft_delete', False)
                )

                with open(detail_screen_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(output)
            except Exception as e:
                print(f"Error generating detail screen stub: {e}")

        # Verifique se a tela de formulário já existe, caso contrário gere um stub
        form_screen_path = os.path.join(output_dir, f'{snake_case}_form_screen.dart')
        if not os.path.exists(form_screen_path):
            try:
                template = self.jinja_env.get_template('screens/form_screen.dart.jinja')
                output = template.render(
                    module_name=module_name,
                    pascal_case=pascal_case,
                    snake_case_name=snake_case,
                    entity_name=pascal_case,
                    fields=module_config.get('fields', []),
                    soft_delete=module_config.get('soft_delete', False)
                )

                with open(form_screen_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(output)
            except Exception as e:
                print(f"Error generating form screen stub: {e}")

    def _has_module_export_enabled(self, module_config):
        """Check if a specific module has export functionality enabled"""
        if isinstance(module_config.get('export'), dict):
            return any(module_config['export'].get(fmt, False) for fmt in ['csv', 'xlsx', 'pdf'])
        return module_config.get('export') is True

    def generate_tests(self):
        """Generate test files for SQLite components"""
        try:
            # Create test directories
            test_core_dir = os.path.join(self.app_dir, 'test', 'core', 'data', 'datasources')
            os.makedirs(test_core_dir, exist_ok=True)

            # Generate SQLite service test
            self._generate_sqlite_service_test(test_core_dir)

            # Generate SQLite helper test
            self._generate_sqlite_helper_test(test_core_dir)

            # Generate repository tests for each module
            for module in self.config.get('modules', []):
                module_name = module['name']
                snake_case = self.case_converter.to_snake_case(module_name)
                module_test_dir = os.path.join(
                    self.app_dir,
                    'test',
                    'features',
                    snake_case,
                    'data',
                    'repositories'
                )
                os.makedirs(module_test_dir, exist_ok=True)

                self._generate_repository_test(module_test_dir, module)
        except Exception as e:
            print(f"Error generating SQLite tests: {e}")

    def _generate_sqlite_service_test(self, output_dir):
        """Generate test for SQLite service"""
        try:
            template = self.jinja_env.get_template('test/core/data/datasources/sqlite_service_test.dart.jinja')
            output = template.render(
                app_name=self.config['app']['name'],
            )

            output_path = os.path.join(output_dir, 'sqlite_service_test.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)
        except Exception as e:
            print(f"Error generating SQLite service test: {e}")

    def _generate_sqlite_helper_test(self, output_dir):
        """Generate test for SQLite helper"""
        try:
            template = self.jinja_env.get_template('test/core/data/datasources/sqlite_helper_test.dart.jinja')
            output = template.render()

            output_path = os.path.join(output_dir, 'sqlite_helper_test.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)
        except Exception as e:
            print(f"Error generating SQLite helper test: {e}")

    def _generate_repository_test(self, output_dir, module_config):
        """Generate test for repository implementation"""
        try:
            module_name = module_config['name']
            pascal_case = self.case_converter.to_pascal_case(module_name)
            snake_case = self.case_converter.to_snake_case(module_name)

            # Corrigido: Usando o caminho sem [module_name]
            template = self.jinja_env.get_template('test/features/repository_impl_test.dart.jinja')
            output = template.render(
                module_name=snake_case,
                pascal_case=pascal_case,
                fields=module_config.get('fields', []),
                soft_delete=module_config.get('soft_delete', False)
            )

            output_path = os.path.join(output_dir, f'{snake_case}_repository_impl_test.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)
        except Exception as e:
            print(f"Error generating repository test for {module_config.get('name', 'unknown')}: {e}")