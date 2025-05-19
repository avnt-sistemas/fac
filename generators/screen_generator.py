import os
from utils.file_manager import FileManager
from utils.case_converter import CaseConverter


class ScreenGenerator:
    def __init__(self, config, project_dir, jinja_env):
        self.config = config
        self.project_dir = project_dir
        self.jinja_env = jinja_env
        self.app_name = config['app']['name']
        self.app_slug = CaseConverter.to_snake_case(self.app_name)

    def generate(self):
        """Gera as telas para cada módulo configurado."""
        for module in self.config.get('modules', []):
            module_name = module['name']
            module_snake = CaseConverter.to_snake_case(module_name)

            # Criar diretórios para o módulo
            feature_dir = os.path.join(self.project_dir, f'lib/features/{module_snake}')
            FileManager.ensure_directory_exists(os.path.join(feature_dir, 'presentation/screens'))
            FileManager.ensure_directory_exists(os.path.join(feature_dir, 'presentation/widgets'))
            FileManager.ensure_directory_exists(os.path.join(feature_dir, 'presentation/provider'))

            # Gerar provider
            provider_template = self.jinja_env.get_template('screens/provider.dart.jinja')
            provider_content = provider_template.render(
                app_name=self.app_slug,
                module=module,
                module_snake=module_snake,
                module_pascal=CaseConverter.to_pascal_case(module_name),
                module_camel=CaseConverter.to_camel_case(module_name)
            )
            FileManager.write_file(
                os.path.join(feature_dir, f'presentation/provider/{module_snake}_provider.dart'),
                provider_content
            )

            # Gerar tela de listagem
            list_template = self.jinja_env.get_template('screens/list_screen.dart.jinja')
            list_content = list_template.render(
                app_name=self.app_slug,
                module=module,
                module_snake=module_snake,
                module_pascal=CaseConverter.to_pascal_case(module_name),
                module_camel=CaseConverter.to_camel_case(module_name)
            )
            FileManager.write_file(
                os.path.join(feature_dir, f'presentation/screens/{module_snake}_list_screen.dart'),
                list_content
            )

            # Gerar tela de detalhes
            detail_template = self.jinja_env.get_template('screens/detail_screen.dart.jinja')
            detail_content = detail_template.render(
                app_name=self.app_slug,
                module=module,
                module_snake=module_snake,
                module_pascal=CaseConverter.to_pascal_case(module_name),
                module_camel=CaseConverter.to_camel_case(module_name)
            )
            FileManager.write_file(
                os.path.join(feature_dir, f'presentation/screens/{module_snake}_detail_screen.dart'),
                detail_content
            )

            # Gerar tela de formulário
            form_template = self.jinja_env.get_template('screens/form_screen.dart.jinja')
            form_content = form_template.render(
                app_name=self.app_slug,
                module=module,
                module_snake=module_snake,
                module_pascal=CaseConverter.to_pascal_case(module_name),
                module_camel=CaseConverter.to_camel_case(module_name)
            )
            FileManager.write_file(
                os.path.join(feature_dir, f'presentation/screens/{module_snake}_form_screen.dart'),
                form_content
            )

        # Gerar Dashboard se habilitado
        if self.config.get('dashboard', {}).get('enabled', False):
            FileManager.ensure_directory_exists(os.path.join(self.project_dir, 'lib/features/dashboard/presentation/screens'))
            FileManager.ensure_directory_exists(os.path.join(self.project_dir, 'lib/features/dashboard/presentation/widgets'))

            dashboard_template = self.jinja_env.get_template('screens/dashboard_screen.dart.jinja')
            dashboard_content = dashboard_template.render(
                app_name=self.app_slug,
                widgets=self.config.get('dashboard', {}).get('widgets', []),
                modules=self.config.get('modules', [])
            )
            FileManager.write_file(
                os.path.join(self.project_dir, 'lib/features/dashboard/presentation/screens/dashboard_screen.dart'),
                dashboard_content
            )