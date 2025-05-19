import os
from utils.file_manager import FileManager
from utils.case_converter import CaseConverter

class TestGenerator:
    def __init__(self, config, project_dir, jinja_env):
        self.config = config
        self.project_dir = project_dir
        self.jinja_env = jinja_env
        self.app_name = config['app']['name']
        self.app_slug = CaseConverter.to_snake_case(self.app_name)

    def generate(self):
        """Gera os testes para o projeto."""
        # Gerar teste de entidade base
        base_entity_test_template = self.jinja_env.get_template('tests/base_entity_test.dart.jinja')
        base_entity_test_content = base_entity_test_template.render(app_name=self.app_slug)
        FileManager.write_file(
            os.path.join(self.project_dir, 'test/domain/entities/base_entity_test.dart'),
            base_entity_test_content
        )

        # Gerar estrutura de mocks
        mocks_template = self.jinja_env.get_template('tests/mocks.dart.jinja')
        mocks_content = mocks_template.render(
            app_name=self.app_slug,
            modules=self.config.get('modules', [])
        )
        FileManager.ensure_directory_exists(os.path.join(self.project_dir, 'test/helpers'))
        FileManager.write_file(
            os.path.join(self.project_dir, 'test/helpers/mocks.dart'),
            mocks_content
        )

        # Gerar fixture reader
        fixture_reader_template = self.jinja_env.get_template('tests/fixture_reader.dart.jinja')
        fixture_reader_content = fixture_reader_template.render()
        FileManager.write_file(
            os.path.join(self.project_dir, 'test/helpers/fixture_reader.dart'),
            fixture_reader_content
        )

        # Gerar diretório de fixtures
        FileManager.ensure_directory_exists(os.path.join(self.project_dir, 'test/fixtures'))

        # Gerar testes para cada módulo
        for module in self.config.get('modules', []):
            module_name = module['name']
            module_snake = CaseConverter.to_snake_case(module_name)

            # Gerar teste de entidade
            entity_test_template = self.jinja_env.get_template('tests/entity_test.dart.jinja')
            entity_test_content = entity_test_template.render(
                app_name=self.app_slug,
                module=module,
                module_snake=module_snake,
                module_pascal=CaseConverter.to_pascal_case(module_name),
                module_camel=CaseConverter.to_camel_case(module_name)
            )
            FileManager.write_file(
                os.path.join(self.project_dir, f'test/domain/entities/{module_snake}_test.dart'),
                entity_test_content
            )

            # Gerar teste de modelo
            model_test_template = self.jinja_env.get_template('tests/model_test.dart.jinja')
            model_test_content = model_test_template.render(
                app_name=self.app_slug,
                module=module,
                module_snake=module_snake,
                module_pascal=CaseConverter.to_pascal_case(module_name),
                module_camel=CaseConverter.to_camel_case(module_name)
            )
            FileManager.ensure_directory_exists(os.path.join(self.project_dir, 'test/data/module'))
            FileManager.write_file(
                os.path.join(self.project_dir, f'test/data/module/{module_snake}_model_test.dart'),
                model_test_content
            )

            # Gerar teste de repositório
            repo_test_template = self.jinja_env.get_template('tests/repository_test.dart.jinja')
            repo_test_content = repo_test_template.render(
                app_name=self.app_slug,
                module=module,
                module_snake=module_snake,
                module_pascal=CaseConverter.to_pascal_case(module_name),
                module_camel=CaseConverter.to_camel_case(module_name)
            )
            FileManager.ensure_directory_exists(os.path.join(self.project_dir, 'test/data/repositories'))
            FileManager.write_file(
                os.path.join(self.project_dir, f'test/data/repositories/{module_snake}_repository_impl_test.dart'),
                repo_test_content
            )

            # Gerar teste de provider
            provider_test_template = self.jinja_env.get_template('tests/provider_test.dart.jinja')
            provider_test_content = provider_test_template.render(
                app_name=self.app_slug,
                module=module,
                module_snake=module_snake,
                module_pascal=CaseConverter.to_pascal_case(module_name),
                module_camel=CaseConverter.to_camel_case(module_name)
            )
            FileManager.ensure_directory_exists(
                os.path.join(self.project_dir, f'test/features/{module_snake}/presentation/provider'))
            FileManager.write_file(
                os.path.join(self.project_dir,
                             f'test/features/{module_snake}/presentation/provider/{module_snake}_provider_test.dart'),
                provider_test_content
            )

            # Gerar teste de widget para tela de listagem
            list_screen_test_template = self.jinja_env.get_template('tests/list_screen_test.dart.jinja')
            list_screen_test_content = list_screen_test_template.render(
                app_name=self.app_slug,
                module=module,
                module_snake=module_snake,
                module_pascal=CaseConverter.to_pascal_case(module_name),
                module_camel=CaseConverter.to_camel_case(module_name)
            )
            FileManager.ensure_directory_exists(
                os.path.join(self.project_dir, f'test/features/{module_snake}/presentation/screens'))
            FileManager.write_file(
                os.path.join(self.project_dir,
                             f'test/features/{module_snake}/presentation/screens/{module_snake}_list_screen_test.dart'),
                list_screen_test_content
            )

            # Gerar fixture JSON para o módulo
            fixture_template = self.jinja_env.get_template('tests/fixture.json.jinja')
            fixture_content = fixture_template.render(module=module)
            FileManager.write_file(
                os.path.join(self.project_dir, f'test/fixtures/{module_snake}.json'),
                fixture_content
            )

        # Gerar teste de integração
        integration_test_template = self.jinja_env.get_template('tests/app_test.dart.jinja')
        integration_test_content = integration_test_template.render(
            app_name=self.app_slug,
            auth_enabled=self.config.get('auth', {}).get('enabled', False),
            modules=self.config.get('modules', [])
        )
        FileManager.write_file(
            os.path.join(self.project_dir, 'integration_test/app_test.dart'),
            integration_test_content
        )