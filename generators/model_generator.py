import os
from jinja2 import Environment, FileSystemLoader, exceptions as jinja2_exceptions
from utils.case_converter import CaseConverter


class ModelGenerator:
    def __init__(self, app_dir, config=None):
        self.app_dir = app_dir
        self.case_converter = CaseConverter()
        self.config = config

        # Set up Jinja2 environment
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

        # Check if SQLite is being used
        self.use_sqlite = config and config.get('persistence', {}).get('provider') == 'sqlite' if config else False

        # Analyze relationships from all modules
        self.modules_config = config.get('modules', []) if config else []
        self.relationships = self._analyze_relationships()

    def _analyze_relationships(self):
        """Analisa os módulos e identifica relacionamentos"""
        relationships = {}

        for module in self.modules_config:
            module_name = module.get('name')
            relationships[module_name] = {
                'direct': [],  # Relacionamentos que este módulo possui (FK)
                'reverse': []  # Relacionamentos onde este módulo é referenciado
            }

            # Analisar campos de referência
            for field in module.get('fields', []):
                if field.get('type') == 'reference':
                    reference_module = field.get('reference')
                    if reference_module:
                        relationships[module_name]['direct'].append({
                            'to_module': reference_module,
                            'field_name': field.get('name'),
                            'pascal_name': self.case_converter.to_pascal_case(field.get('name').replace('Id', '')),
                            'camel_name': self.case_converter.to_camel_case(field.get('name').replace('Id', '')),
                            'required': field.get('required', False)
                        })

        # Encontrar relacionamentos reversos
        for module_name, module_rels in relationships.items():
            for rel in module_rels['direct']:
                target_module = rel['to_module']
                if target_module in relationships:
                    # Criar um nome único para o relacionamento reverso baseado no campo
                    field_base_name = rel['field_name'].replace('Id', '')

                    # Adicionar o relacionamento reverso com nome único
                    relationships[target_module]['reverse'].append({
                        'from_module': module_name,
                        'field_name': rel['field_name'],
                        'reverse_name': f"{module_name.lower()}ListAs{field_base_name.capitalize()}",
                        'required': rel['required']
                    })

        return relationships

    def get_module_relationships(self, module_name):
        """Retorna os relacionamentos de um módulo específico"""
        return self.relationships.get(module_name, {'direct': [], 'reverse': []})

    def get_dependency_order(self):
        """Retorna a ordem de criação baseada nas dependências"""
        dependency_graph = {}
        all_modules = set()

        # Construir grafo de dependências
        for module in self.modules_config:
            module_name = module.get('name')
            all_modules.add(module_name)
            dependency_graph[module_name] = []

            for field in module.get('fields', []):
                if field.get('type') == 'reference':
                    reference = field.get('reference')
                    if reference:
                        dependency_graph[module_name].append(reference)

        # Ordenação topológica
        visited = set()
        temp_visited = set()
        result = []

        def visit(module):
            if module in temp_visited:
                return False  # Dependência circular
            if module in visited:
                return True

            temp_visited.add(module)

            for dependency in dependency_graph.get(module, []):
                if not visit(dependency):
                    return False

            temp_visited.remove(module)
            visited.add(module)
            result.append(module)
            return True

        # Processar todos os módulos
        for module in all_modules:
            if module not in visited:
                if not visit(module):
                    print(f"Warning: Circular dependency detected involving {module}")
                    # Em caso de dependência circular, usar ordem original
                    result = [m.get('name') for m in self.modules_config]
                    break

        return result

    def generate_relationship_imports(self, module_name):
        relationships = self.get_module_relationships(module_name)
        imports = []
        imported_modules = set()

        for rel in relationships['direct']:
            related_module = rel['to_module']
            if related_module not in imported_modules:
                snake_case = self.case_converter.to_snake_case(related_module)
                imports.append(f"import '../../../{snake_case}/domain/entities/{snake_case}_entity.dart';")
                imported_modules.add(related_module)

        # Para relacionamentos reversos, também precisamos dos imports
        for rel in relationships['reverse']:
            related_module = rel['from_module']
            if related_module not in imported_modules:
                snake_case = self.case_converter.to_snake_case(related_module)
                imports.append(f"import '../../../{snake_case}/domain/entities/{snake_case}_entity.dart';")
                imported_modules.add(related_module)

        return imports

    def print_relationships_summary(self):
        """Imprime um resumo dos relacionamentos identificados"""
        print("\n=== RELATIONSHIP SUMMARY ===")

        for module in self.modules_config:
            module_name = module.get('name')
            relationships = self.get_module_relationships(module_name)

            if relationships['direct'] or relationships['reverse']:
                print(f"\n{module_name}:")

                for rel in relationships['direct']:
                    print(f"  → {rel['to_module']} (via {rel['field_name']})")

                for rel in relationships['reverse']:
                    print(f"  ← {rel['from_module']} (has many as {rel['reverse_name']})")

        dependency_order = self.get_dependency_order()
        print(f"\nDependency Order: {' → '.join(dependency_order)}")
        print("=" * 30)

    def generate_all_modules(self):
        """Gera todos os módulos na ordem correta de dependências"""
        self.print_relationships_summary()

        dependency_order = self.get_dependency_order()
        modules_dict = {module.get('name'): module for module in self.modules_config}

        for module_name in dependency_order:
            if module_name in modules_dict:
                module_config = modules_dict[module_name]
                self.generate_module(module_config)

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

        # Get relationships for this module
        relationships = self.get_module_relationships(module_name)
        related_imports = self.generate_relationship_imports(module_name)

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

        # Generate entity with relationships
        self._generate_entity(module_dir, module_name, pascal_case, module_config, relationships, related_imports)

        # Generate model with relationships
        self._generate_model(module_dir, module_name, pascal_case, module_config, relationships, related_imports)

        # Generate repository interface
        self._generate_repository_interface(module_dir, module_name, pascal_case,
                                            module_config.get('soft_delete', False))

        # Generate repository implementation
        self._generate_repository_implementation(module_dir, module_name, pascal_case, module_config)

        # Generate usecases
        self._generate_usecases(module_dir, module_name, pascal_case, module_config.get('soft_delete', False))

        # Generate controller
        self._generate_controller(module_dir, module_name, pascal_case, module_config.get('soft_delete', False))

        # Generate screens
        self._generate_screens(module_dir, module_name, pascal_case, module_config)

        # Generate relationship helpers if needed
        if relationships['direct'] or relationships['reverse']:
            self._generate_relationship_helpers(module_dir, module_name, pascal_case, module_config, relationships)

        print(f"Module {module_name} generated successfully.")

    def _generate_entity(self, module_dir, module_name, pascal_case, module_config, relationships, related_imports):
        """Generate the entity class for the module with relationships"""
        try:
            template = self.jinja_env.get_template('module/entity.dart.jinja')

            # Processar relacionamentos reversos para evitar duplicação
            processed_reverse = []
            seen_combinations = set()

            for rel in relationships['reverse']:
                # Usar o reverse_name único que criamos
                rel_copy = rel.copy()
                rel_copy['property_name'] = self.case_converter.to_pascal_case(rel['reverse_name'])
                rel_copy['camel_name'] = self.case_converter.to_camel_case(rel['reverse_name'])
                processed_reverse.append(rel_copy)

            adjusted_relationships = {
                'direct': relationships['direct'],
                'reverse': processed_reverse
            }

            output = template.render(
                module_name=module_name,
                pascal_case=pascal_case,
                fields=module_config.get('fields', []),
                soft_delete=module_config.get('soft_delete', False),
                relationships=adjusted_relationships,
                related_imports=related_imports,
                has_relationships=len(relationships['direct']) > 0 or len(relationships['reverse']) > 0
            )

            output_path = os.path.join(module_dir, 'domain', 'entities',
                                       f'{self.case_converter.to_snake_case(module_name)}_entity.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

            print(f"Generated entity for {module_name}")
        except Exception as e:
            print(f"Error generating entity for {module_name}: {e}")

    def _generate_model(self, module_dir, module_name, pascal_case, module_config, relationships, related_imports):
        """Generate the model class for the module with relationships"""
        try:
            template = self.jinja_env.get_template('module/model.dart.jinja')

            # Processar relacionamentos reversos com nomes únicos
            processed_reverse = []
            for rel in relationships['reverse']:
                rel_copy = rel.copy()
                rel_copy['property_name'] = self.case_converter.to_pascal_case(rel['reverse_name'])
                rel_copy['camel_name'] = self.case_converter.to_camel_case(rel['reverse_name'])
                processed_reverse.append(rel_copy)

            adjusted_relationships = {
                'direct': relationships['direct'],
                'reverse': processed_reverse
            }

            output = template.render(
                module_name=module_name,
                snake_name=self.case_converter.to_snake_case(module_name),
                pascal_case=pascal_case,
                fields=module_config.get('fields', []),
                soft_delete=module_config.get('soft_delete', False),
                relationships=adjusted_relationships,
                related_imports=related_imports,
                has_relationships=len(relationships['direct']) > 0 or len(relationships['reverse']) > 0
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
            template = self.jinja_env.get_template('module/repository_interface.dart.jinja')
            output = template.render(
                module_name=module_name,
                snake_case=self.case_converter.to_snake_case(module_name),
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
            relationships = self.get_module_relationships(module_name)
            # Processar relacionamentos reversos com nomes únicos
            processed_reverse = []
            for rel in relationships['reverse']:
                rel_copy = rel.copy()
                rel_copy['pascal_name'] = self.case_converter.to_pascal_case(rel['reverse_name'])
                rel_copy['camel_name'] = self.case_converter.to_camel_case(rel['reverse_name'])
                processed_reverse.append(rel_copy)

            adjusted_relationships = {
                'direct': relationships['direct'],
                'reverse': processed_reverse
            }

            if self.use_sqlite:
                from generators.sqlite_generator import SQLiteGenerator
                sqlite_generator = SQLiteGenerator(self.app_dir, self.config)

                output_dir = os.path.join(module_dir, 'data', 'repositories')
                sqlite_generator.generate_repository_impl(module_config, output_dir, adjusted_relationships)
            else:
                template = self.jinja_env.get_template('module/repository_impl.dart.jinja')
                output = template.render(
                    module_name=module_name,
                    pascal_case=pascal_case,
                    persistence_type=module_config.get('persistence', {}).get('provider', 'sqlite'),
                    soft_delete=module_config.get('soft_delete', False),
                    relationships=adjusted_relationships
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
                template = self.jinja_env.get_template(f'module/usecases/{usecase}_usecase.dart.jinja')
                output = template.render(
                    module_name=module_name,
                    snake_name=self.case_converter.to_snake_case(module_name),
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
            template = self.jinja_env.get_template('module/controller.dart.jinja')
            output = template.render(
                module_name=module_name,
                pascal_case=pascal_case,
                snake_case=self.case_converter.to_snake_case(module_name),
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
            has_export = (isinstance(module_config.get('export'), dict) and
                          any(module_config['export'].get(fmt, False) for fmt in
                              ['csv', 'xlsx', 'pdf'])) or module_config.get('export') is True

            if has_export and self.use_sqlite:
                from generators.sqlite_generator import SQLiteGenerator
                sqlite_generator = SQLiteGenerator(self.app_dir, self.config)

                screens_dir = os.path.join(module_dir, 'presentation', 'screens')
                self._generate_standard_screens(module_dir, module_name, pascal_case, module_config)
            else:
                self._generate_standard_screens(module_dir, module_name, pascal_case, module_config)

        except Exception as e:
            print(f"Error generating screens for {module_name}: {e}")
            self._generate_standard_screens(module_dir, module_name, pascal_case, module_config)

    def _generate_standard_screens(self, module_dir, module_name, pascal_case, module_config):
        """Generate the standard screens for the module"""
        try:
            screens = [
                ('list_screen.dart.jinja', 'list'),
                ('detail_screen.dart.jinja', 'detail'),
                ('form_screen.dart.jinja', 'form')
            ]

            snake_case_name = self.case_converter.to_snake_case(module_name)

            # Get relationships with adjusted names
            relationships = self.get_module_relationships(module_name)
            processed_reverse = []
            for rel in relationships['reverse']:
                rel_copy = rel.copy()
                rel_copy['property_name'] = self.case_converter.to_pascal_case(rel['reverse_name'])
                rel_copy['camel_name'] = self.case_converter.to_camel_case(rel['reverse_name'])
                rel_copy['snake_name'] = self.case_converter.to_snake_case(rel['from_module'])
                processed_reverse.append(rel_copy)

            adjusted_relationships = {
                'direct': relationships['direct'],
                'reverse': processed_reverse
            }

            for template_file, screen_type in screens:
                try:
                    template_path = f'screens/{template_file}'
                    template = self.jinja_env.get_template(template_path)

                    output = template.render(
                        module_name=module_name,
                        pascal_case=pascal_case,
                        snake_case_name=snake_case_name,
                        entity_name=pascal_case,
                        fields=module_config.get('fields', []),
                        soft_delete=module_config.get('soft_delete', False),
                        relationships=adjusted_relationships,
                        has_relationships=len(relationships['direct']) > 0 or len(relationships['reverse']) > 0
                    )

                    output_path = os.path.join(module_dir, 'presentation', 'screens',
                                               f'{snake_case_name}_{screen_type}_screen.dart')
                    with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                        f.write(output)

                    print(f"Generated {screen_type} screen for {module_name}")

                    if screen_type == 'form':
                        create_path = os.path.join(module_dir, 'presentation', 'screens',
                                                   f'{snake_case_name}_create_screen.dart')
                        with open(create_path, 'w', encoding='utf-8', newline='\n') as f:
                            f.write(f"""import 'package:flutter/material.dart';
import './{snake_case_name}_form_screen.dart';

class {pascal_case}CreateScreen extends StatelessWidget {{
  const {pascal_case}CreateScreen({{super.key}}) ;

  @override
  Widget build(BuildContext context) {{
    return {pascal_case}FormScreen(
      isEditing: false,
    );
  }}
}}""")
                        print(f"Generated create screen for {module_name}")

                        edit_path = os.path.join(module_dir, 'presentation', 'screens',
                                                 f'{snake_case_name}_edit_screen.dart')
                        with open(edit_path, 'w', encoding='utf-8', newline='\n') as f:
                            f.write(f"""import 'package:flutter/material.dart';
import '../../domain/entities/{snake_case_name}_entity.dart';
import './{snake_case_name}_form_screen.dart';

class {pascal_case}EditScreen extends StatelessWidget {{
  const {pascal_case}EditScreen({{super.key}}) ;

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

    def _generate_relationship_helpers(self, module_dir, module_name, pascal_case, module_config, relationships):
        """Gera arquivos auxiliares para gerenciar relacionamentos"""
        try:
            snake_case = self.case_converter.to_snake_case(module_name)

            # Gerar service de relacionamentos
            self._generate_relationship_service(module_dir, module_name, pascal_case, relationships)

            # Gerar queries específicas de relacionamento para SQLite
            if self.use_sqlite:
                self._generate_relationship_queries(module_dir, module_name, pascal_case, relationships)

        except Exception as e:
            print(f"Error generating relationship helpers for {module_name}: {e}")

    def _generate_relationship_service(self, module_dir, module_name, pascal_case, relationships):
        """Gera service para operações com relacionamentos"""
        try:
            template = self.jinja_env.get_template('module/relationship/relationship_service.dart.jinja')

            # Processar relacionamentos reversos com nomes únicos
            processed_reverse = []
            for rel in relationships['reverse']:
                rel_copy = rel.copy()
                rel_copy['pascal_name'] = self.case_converter.to_pascal_case(rel['reverse_name'])
                rel_copy['camel_name'] = self.case_converter.to_camel_case(rel['reverse_name'])
                rel_copy['snake_name'] = self.case_converter.to_snake_case(rel['from_module'])
                processed_reverse.append(rel_copy)

            adjusted_relationships = {
                'direct': relationships['direct'],
                'reverse': processed_reverse
            }

            print(f"Generating relationship service for {module_name}")
            print(adjusted_relationships)

            output = template.render(
                snake_case=self.case_converter.to_snake_case(module_name),
                module_name=module_name,
                pascal_case=pascal_case,
                snake_case_name=self.case_converter.to_snake_case(module_name),
                relationships=adjusted_relationships
            )

            service_dir = os.path.join(module_dir, 'data', 'services')
            os.makedirs(service_dir, exist_ok=True)

            output_path = os.path.join(service_dir,
                                       f'{self.case_converter.to_snake_case(module_name)}_relationship_service.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

            print(f"Generated relationship service for {module_name}")

        except Exception as e:
            print(f"Error generating relationship service for {module_name}: {e}")

    def _generate_relationship_queries(self, module_dir, module_name, pascal_case, relationships):
        """Gera queries SQL específicas para relacionamentos"""
        try:
            template = self.jinja_env.get_template('module/relationship/relationship_queries.dart.jinja')

            # Processar relacionamentos reversos com nomes únicos
            processed_reverse = []
            for rel in relationships['reverse']:
                rel_copy = rel.copy()
                rel_copy['query_name'] = f"get{rel['reverse_name'].capitalize()}"
                rel_copy['property_name'] = self.case_converter.to_pascal_case(rel['reverse_name'])
                rel_copy['camel_name'] = self.case_converter.to_camel_case(rel['reverse_name'])
                processed_reverse.append(rel_copy)

            adjusted_relationships = {
                'direct': relationships['direct'],
                'reverse': processed_reverse
            }

            output = template.render(
                module_name=module_name,
                pascal_case=pascal_case,
                snake_case_name=self.case_converter.to_snake_case(module_name),
                relationships=adjusted_relationships
            )

            queries_dir = os.path.join(module_dir, 'data', 'queries')
            os.makedirs(queries_dir, exist_ok=True)

            output_path = os.path.join(queries_dir,
                                       f'{self.case_converter.to_snake_case(module_name)}_relationship_queries.dart')
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

            print(f"Generated relationship queries for {module_name}")

        except Exception as e:
            print(f"Error generating relationship queries for {module_name}: {e}")