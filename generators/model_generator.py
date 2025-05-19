import os
from jinja2 import Environment, FileSystemLoader, exceptions as jinja2_exceptions
from utils.case_converter import CaseConverter


class ModelGenerator:
    def __init__(self, app_dir, config=None):  # Adicionado config como parâmetro
        self.app_dir = app_dir
        self.case_converter = CaseConverter()
        self.config = config  # Salvar a configuração para uso posterior

        # Set up Jinja2 environment
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

        # Check if SQLite is being used
        self.use_sqlite = config and config.get('persistence', {}).get('provider') == 'sqlite' if config else False

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
        self._generate_repository_interface(module_dir, module_name, pascal_case, module_config.get('soft_delete', False))

        # Generate repository implementation
        self._generate_repository_implementation(module_dir, module_name, pascal_case, module_config)

        # Generate usecases
        self._generate_usecases(module_dir, module_name, pascal_case, module_config.get('soft_delete', False))

        # Generate controller
        self._generate_controller(module_dir, module_name, pascal_case, module_config.get('soft_delete', False))

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
                fields=module_config.get('fields', []),
                soft_delete=module_config.get('soft_delete', False)
            )

            output_path = os.path.join(module_dir, 'domain', 'entities',
                                       f'{self.case_converter.to_snake_case(module_name)}_entity.dart')
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

            output_path = os.path.join(module_dir, 'data', 'models',
                                       f'{self.case_converter.to_snake_case(module_name)}_model.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

            print(f"Generated model for {module_name}")
        except Exception as e:
            print(f"Error generating model for {module_name}: {e}")

    def _generate_repository_interface(self, module_dir, module_name, pascal_case, soft_delete):
        """Generate the repository interface for the module"""
        try:
            # Use module/repository_interface.dart.jinja
            template = self.jinja_env.get_template('module/repository_interface.dart.jinja')
            output = template.render(
                module_name=module_name,
                pascal_case=pascal_case,
                soft_delete=soft_delete
            )

            output_path = os.path.join(module_dir, 'domain', 'repositories',
                                       f'i_{self.case_converter.to_snake_case(module_name)}_repository.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

            print(f"Generated repository interface for {module_name}")
        except Exception as e:
            print(f"Error generating repository interface for {module_name}: {e}")

    def _generate_repository_implementation(self, module_dir, module_name, pascal_case, module_config):
        """Generate the repository implementation for the module"""
        try:
            # Determine the template to use based on persistence provider
            if self.use_sqlite:
                # If using SQLite, call the SQLiteGenerator to generate the repository
                from generators.sqlite_generator import SQLiteGenerator
                sqlite_generator = SQLiteGenerator(self.app_dir, self.config)

                output_dir = os.path.join(module_dir, 'data', 'repositories')
                sqlite_generator.generate_repository_impl(module_config, output_dir)
            else:
                # Use the standard repository implementation
                template = self.jinja_env.get_template('module/repository_impl.dart.jinja')
                output = template.render(
                    module_name=module_name,
                    pascal_case=pascal_case,
                    persistence_type=module_config.get('persistence', {}).get('provider', 'sqlite'),
                    soft_delete=module_config.get('soft_delete', False)
                )

                output_path = os.path.join(module_dir, 'data', 'repositories',
                                           f'{self.case_converter.to_snake_case(module_name)}_repository_impl.dart')
                with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(output)

                print(f"Generated repository implementation for {module_name}")
        except Exception as e:
            print(f"Error generating repository implementation for {module_name}: {e}")

    def _generate_usecases(self, module_dir, module_name, pascal_case, soft_delete):
        """Generate the usecases for the module"""
        try:
            usecases = ['create', 'delete', 'get_all', 'get_by_id', 'update']

            if soft_delete:
                usecases = usecases + ['hard_delete', 'restore', 'get_all_with_deleted']

            for usecase in usecases:
                # Use module/usecases/{usecase}_usecase.dart.jinja
                template = self.jinja_env.get_template(f'module/usecases/{usecase}_usecase.dart.jinja')
                output = template.render(
                    module_name=module_name,
                    pascal_case=pascal_case,
                    soft_delete=soft_delete
                )

                output_path = os.path.join(module_dir, 'domain', 'usecases',
                                           f'{usecase}_{self.case_converter.to_snake_case(module_name)}_usecase.dart')
                with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(output)

            print(f"Generated usecases for {module_name}")
        except Exception as e:
            print(f"Error generating usecases for {module_name}: {e}")

    def _generate_controller(self, module_dir, module_name, pascal_case, soft_delete):
        """Generate the controller for the module"""
        try:
            # Use module/controller.dart.jinja
            template = self.jinja_env.get_template('module/controller.dart.jinja')
            output = template.render(
                module_name=module_name,
                pascal_case=pascal_case,
                soft_delete=soft_delete
            )

            output_path = os.path.join(module_dir, 'presentation', 'controllers',
                                       f'{self.case_converter.to_snake_case(module_name)}_controller.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

            print(f"Generated controller for {module_name}")
        except Exception as e:
            print(f"Error generating controller for {module_name}: {e}")

    def _generate_screens(self, module_dir, module_name, pascal_case, module_config):
        """Generate the screens for the module"""
        try:
            # Verificar se o módulo tem exportação habilitada
            has_export = (isinstance(module_config.get('export'), dict) and
                          any(module_config['export'].get(fmt, False) for fmt in
                              ['csv', 'xlsx', 'pdf'])) or module_config.get('export') is True

            # Se o módulo tem exportação habilitada e estamos usando SQLite, gerar a tela de listagem com exportação
            if has_export and self.use_sqlite:
                # Use SQLiteGenerator para gerar a tela de listagem com suporte a exportação
                from generators.sqlite_generator import SQLiteGenerator
                sqlite_generator = SQLiteGenerator(self.app_dir, self.config)

                screens_dir = os.path.join(module_dir, 'presentation', 'screens')
                # list_screen_generated = sqlite_generator.generate_list_screen_with_export(
                #     module_config, screens_dir)
                #
                # # Se a tela de listagem foi gerada com sucesso, não precisamos gerar a tela padrão
                # if list_screen_generated:
                #     print(f"Generated list screen with export for {module_name}")
                # else:
                    # Fallback para a tela de listagem padrão
                self._generate_standard_screens(module_dir, module_name, pascal_case, module_config)
            else:
                # Gerar telas padrão
                self._generate_standard_screens(module_dir, module_name, pascal_case, module_config)

        except Exception as e:
            print(f"Error generating screens for {module_name}: {e}")
            # Fallback para a geração de telas padrão
            self._generate_standard_screens(module_dir, module_name, pascal_case, module_config)

    def _generate_standard_screens(self, module_dir, module_name, pascal_case, module_config):
        """Generate the standard screens for the module"""
        try:
            # We should create templates for these screen files
            screens = [
                ('list_screen.dart.jinja', 'list'),
                ('detail_screen.dart.jinja', 'detail'),
                ('form_screen.dart.jinja', 'form')  # Usando form_screen para create e edit
            ]

            snake_case_name = self.case_converter.to_snake_case(module_name)

            for template_file, screen_type in screens:
                try:
                    template_path = f'screens/{template_file}'
                    template = self.jinja_env.get_template(template_path)

                    output = template.render(
                        module_name=module_name,
                        pascal_case=pascal_case,
                        snake_case_name=snake_case_name,
                        entity_name=pascal_case,  # Adicione isso para compatibilidade com seu template
                        fields=module_config.get('fields', []),
                        soft_delete=module_config.get('soft_delete', False)
                    )

                    output_path = os.path.join(module_dir, 'presentation', 'screens',
                                               f'{snake_case_name}_{screen_type}_screen.dart')
                    with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                        f.write(output)

                    print(f"Generated {screen_type} screen for {module_name}")

                    # Se form_screen for encontrado, usá-lo para criar também as telas create e edit
                    if screen_type == 'form':
                        # Criar a tela de criação
                        create_path = os.path.join(module_dir, 'presentation', 'screens',
                                                   f'{snake_case_name}_create_screen.dart')
                        with open(create_path, 'w', encoding='utf-8', newline='\n') as f:
                            f.write(f"""import 'package:flutter/material.dart';
import './{snake_case_name}_form_screen.dart';

class {pascal_case}CreateScreen extends StatelessWidget {{
  const {pascal_case}CreateScreen({{Key? key}}) : super(key: key);

  @override
  Widget build(BuildContext context) {{
    return {pascal_case}FormScreen(
      isEditing: false,
    );
  }}
}}""")
                        print(f"Generated create screen for {module_name}")

                        # Criar a tela de edição
                        edit_path = os.path.join(module_dir, 'presentation', 'screens',
                                                 f'{snake_case_name}_edit_screen.dart')
                        with open(edit_path, 'w', encoding='utf-8', newline='\n') as f:
                            f.write(f"""import 'package:flutter/material.dart';
import '../../domain/entities/{snake_case_name}_entity.dart';
import './{snake_case_name}_form_screen.dart';

class {pascal_case}EditScreen extends StatelessWidget {{
  const {pascal_case}EditScreen({{Key? key}}) : super(key: key);

  @override
  Widget build(BuildContext context) {{
    final {pascal_case}Entity item = ModalRoute.of(context)!.settings.arguments as {pascal_case}Entity;

    return {pascal_case}FormScreen(
      item: item,
      isEditing: true,
    );
  }}
}}""")
                        print(f"Generated edit screen for {module_name}")

                except jinja2_exceptions.TemplateNotFound:
                    print(f"Warning: Template 'screens/{template_file}' not found, skipping")
                except Exception as e:
                    print(f"Error generating {screen_type} screen for {module_name}: {e}")

        except Exception as e:
            print(f"Error generating screens for {module_name}: {e}")