import os
from jinja2 import Environment, FileSystemLoader
from utils.case_converter import CaseConverter

class ModelGenerator:
    def __init__(self, app_dir):
        self.app_dir = app_dir
        self.case_converter = CaseConverter()

        # Set up Jinja2 environment
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def generate_module(self, module_config):
        """Generate all files for a module"""
        module_name = module_config.get('name')
        if not module_name:
            print("Warning: Module config missing 'name' field.")
            return

        print(f"Generating module: {module_name}")

        # Convert module name to various cases
        snake_case = self.case_converter.to_snake_case(module_name)
        camel_case = self.case_converter.to_camel_case(module_name)
        pascal_case = self.case_converter.to_pascal_case(module_name)

        # Create module directories
        module_dir = os.path.join(self.app_dir, 'lib', 'features', snake_case)
        os.makedirs(os.path.join(module_dir, 'data', 'models'), exist_ok=True)
        os.makedirs(os.path.join(module_dir, 'data', 'repositories'), exist_ok=True)
        os.makedirs(os.path.join(module_dir, 'domain', 'entities'), exist_ok=True)
        os.makedirs(os.path.join(module_dir, 'domain', 'repositories'), exist_ok=True)
        os.makedirs(os.path.join(module_dir, 'domain', 'usecases'), exist_ok=True)
        os.makedirs(os.path.join(module_dir, 'presentation', 'controllers'), exist_ok=True)
        os.makedirs(os.path.join(module_dir, 'presentation', 'screens'), exist_ok=True)
        os.makedirs(os.path.join(module_dir, 'presentation', 'widgets'), exist_ok=True)

        # Generate entity
        self._generate_entity(module_dir, module_name, pascal_case, module_config)

        # Generate model
        self._generate_model(module_dir, module_name, pascal_case, module_config)

        # Generate repository interface
        self._generate_repository_interface(module_dir, module_name, pascal_case)

        # Generate repository implementation
        self._generate_repository_implementation(module_dir, module_name, pascal_case, module_config)

        # Generate usecases
        self._generate_usecases(module_dir, module_name, pascal_case)

        # Generate controller
        self._generate_controller(module_dir, module_name, pascal_case)

        # Generate screens
        self._generate_screens(module_dir, module_name, pascal_case, module_config)

        print(f"Module {module_name} generated successfully.")

    def _generate_entity(self, module_dir, module_name, pascal_case, module_config):
        """Generate the entity class for the module"""
        try:
            # Use module/entity.dart.jinja
            template = self.jinja_env.get_template('module/entity.dart.jinja')
            output = template.render(
                module_name=module_name,
                pascal_case=pascal_case,
                fields=module_config.get('fields', [])
            )

            output_path = os.path.join(module_dir, 'domain', 'entities', f'{self.case_converter.to_snake_case(module_name)}_entity.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

            print(f"Generated entity for {module_name}")
        except Exception as e:
            print(f"Error generating entity for {module_name}: {e}")

    def _generate_model(self, module_dir, module_name, pascal_case, module_config):
        """Generate the model class for the module"""
        try:
            # Use module/model.dart.jinja
            template = self.jinja_env.get_template('module/model.dart.jinja')
            output = template.render(
                module_name=module_name,
                pascal_case=pascal_case,
                fields=module_config.get('fields', [])
            )

            output_path = os.path.join(module_dir, 'data', 'models', f'{self.case_converter.to_snake_case(module_name)}_model.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

            print(f"Generated model for {module_name}")
        except Exception as e:
            print(f"Error generating model for {module_name}: {e}")

    def _generate_repository_interface(self, module_dir, module_name, pascal_case):
        """Generate the repository interface for the module"""
        try:
            # Use module/repository_interface.dart.jinja
            template = self.jinja_env.get_template('module/repository_interface.dart.jinja')
            output = template.render(
                module_name=module_name,
                pascal_case=pascal_case
            )

            output_path = os.path.join(module_dir, 'domain', 'repositories', f'i_{self.case_converter.to_snake_case(module_name)}_repository.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

            print(f"Generated repository interface for {module_name}")
        except Exception as e:
            print(f"Error generating repository interface for {module_name}: {e}")

    def _generate_repository_implementation(self, module_dir, module_name, pascal_case, module_config):
        """Generate the repository implementation for the module"""
        try:
            # Use module/repository_impl.dart.jinja
            template = self.jinja_env.get_template('module/repository_impl.dart.jinja')
            output = template.render(
                module_name=module_name,
                pascal_case=pascal_case,
                persistence_type=module_config.get('persistence', {}).get('provider', 'sqlite'),
                soft_delete=module_config.get('soft_delete', False)
            )

            output_path = os.path.join(module_dir, 'data', 'repositories', f'{self.case_converter.to_snake_case(module_name)}_repository_impl.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

            print(f"Generated repository implementation for {module_name}")
        except Exception as e:
            print(f"Error generating repository implementation for {module_name}: {e}")

    def _generate_usecases(self, module_dir, module_name, pascal_case):
        """Generate the usecases for the module"""
        try:
            usecases = ['get_all', 'get_by_id', 'create', 'update', 'delete']

            for usecase in usecases:
                # Use module/usecases/{usecase}_usecase.dart.jinja
                template = self.jinja_env.get_template(f'module/usecases/{usecase}_usecase.dart.jinja')
                output = template.render(
                    module_name=module_name,
                    pascal_case=pascal_case
                )

                output_path = os.path.join(module_dir, 'domain', 'usecases', f'{usecase}_{self.case_converter.to_snake_case(module_name)}_usecase.dart')
                with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(output)

            print(f"Generated usecases for {module_name}")
        except Exception as e:
            print(f"Error generating usecases for {module_name}: {e}")

    def _generate_controller(self, module_dir, module_name, pascal_case):
        """Generate the controller for the module"""
        try:
            # Use module/controller.dart.jinja
            template = self.jinja_env.get_template('module/controller.dart.jinja')
            output = template.render(
                module_name=module_name,
                pascal_case=pascal_case
            )

            output_path = os.path.join(module_dir, 'presentation', 'controllers', f'{self.case_converter.to_snake_case(module_name)}_controller.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

            print(f"Generated controller for {module_name}")
        except Exception as e:
            print(f"Error generating controller for {module_name}: {e}")

    def _generate_screens(self, module_dir, module_name, pascal_case, module_config):
        """Generate the screens for the module"""
        try:
            # We should create templates for these screen files
            screens = [
                ('list_screen.dart.jinja', 'list'),
                ('detail_screen.dart.jinja', 'detail'),
                ('create_screen.dart.jinja', 'create'),
                ('edit_screen.dart.jinja', 'edit')
            ]

            for template_file, screen_type in screens:
                try:
                    template_path = f'screens/{template_file}'
                    if not self.jinja_env.loader.exists(template_path):
                        print(f"Warning: Template {template_path} not found, skipping")
                        continue

                    template = self.jinja_env.get_template(template_path)
                    output = template.render(
                        module_name=module_name,
                        pascal_case=pascal_case,
                        fields=module_config.get('fields', []),
                        exports=module_config.get('export', {})
                    )

                    output_path = os.path.join(module_dir, 'presentation', 'screens', f'{self.case_converter.to_snake_case(module_name)}_{screen_type}_screen.dart')
                    with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                        f.write(output)

                    print(f"Generated {screen_type} screen for {module_name}")
                except Exception as e:
                    print(f"Error generating {screen_type} screen for {module_name}: {e}")

        except Exception as e:
            print(f"Error generating screens for {module_name}: {e}")