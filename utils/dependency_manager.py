from typing import List, Dict, Optional, Set
import os


class DependencyManager:
    """
    Gerenciador de dependências que usa flutter pub add para manter
    o pubspec.yaml sempre atualizado com as versões mais recentes.
    """

    def __init__(self, flutter_cli, config: Dict):
        self.flutter_cli = flutter_cli
        self.config = config

        # Mapeamento de dependências baseado em features
        self.dependency_map = {
            # Dependências base (sempre incluídas)
            'base': [
                'provider',  # State management
                'get_it',  # Dependency injection
                'dio',  # HTTP client
                'equatable',  # Value equality
                'shared_preferences',  # Local storage
                'intl',  # Internationalization
            ],

            # Dependências para SQLite
            'sqlite': [
                'sqflite',
                'path',
                'uuid',
                'path_provider',
            ],

            # Dependências para Firebase
            'firebase': [
                'firebase_core',
                'cloud_firestore',
                'firebase_storage',
            ],

            # Dependências para autenticação
            'auth_base': [
                'flutter_secure_storage',
            ],

            'auth_firebase': [
                'firebase_auth',
                'google_sign_in',
            ],

            # Dependências para UI
            'ui': [
                'flutter_svg',
                'google_fonts',
            ],

            # Dependências para gráficos/dashboard
            'charts': [
                'fl_chart',
            ],

            # Dependências para export
            'export_pdf': ['pdf'],
            'export_excel': ['excel'],
            'export_csv': ['csv'],
            'export_share': ['open_file'],

            # Dependências para desenvolvimento
            'dev': [
                'flutter_lints',
                'mockito',
                'bloc_test',
                'build_runner',
            ]
        }

    def get_required_dependencies(self) -> Dict[str, List[str]]:
        """
        Determina quais dependências são necessárias baseado na configuração.

        Returns:
            Dict com 'dependencies' e 'dev_dependencies'
        """
        dependencies = set(self.dependency_map['base'])
        dev_dependencies = set(self.dependency_map['dev'])

        # Adiciona dependências de UI
        dependencies.update(self.dependency_map['ui'])

        # Dependências de persistência
        persistence_provider = self.config.get('persistence', {}).get('provider', 'sqlite')
        if persistence_provider == 'sqlite':
            dependencies.update(self.dependency_map['sqlite'])
        elif persistence_provider == 'firebase':
            dependencies.update(self.dependency_map['firebase'])

        # Dependências de autenticação
        if self.config.get('auth', {}).get('enabled', False):
            dependencies.update(self.dependency_map['auth_base'])

            auth_provider = self.config.get('auth', {}).get('provider', 'firebase')
            if auth_provider == 'firebase':
                dependencies.update(self.dependency_map['auth_firebase'])
                dependencies.update(self.dependency_map['firebase'])  # Firebase core

        # Dependências de dashboard
        if self.config.get('dashboard', {}).get('enabled', False):
            dependencies.update(self.dependency_map['charts'])

        # Dependências de export
        export_types = set()
        for module in self.config.get('modules', []):
            exports = module.get('export', {})
            if exports.get('pdf', False):
                export_types.add('pdf')
            if exports.get('csv', False):
                export_types.add('csv')
            if exports.get('xlsx', False):
                export_types.add('excel')

        # Adiciona dependências de export
        for export_type in export_types:
            key = f'export_{export_type}'
            if key in self.dependency_map:
                dependencies.update(self.dependency_map[key])

        # Se há qualquer export, adiciona dependência de share
        if export_types:
            dependencies.update(self.dependency_map['export_share'])

        return {
            'dependencies': list(dependencies),
            'dev_dependencies': list(dev_dependencies)
        }

    def install_dependencies(self, project_dir: str):
        """
        Instala todas as dependências necessárias usando flutter pub add.

        Args:
            project_dir (str): Diretório do projeto Flutter
        """
        required_deps = self.get_required_dependencies()

        print("Installing dependencies...")

        # Instala dependências normais
        if required_deps['dependencies']:
            print(f"Adding dependencies: {', '.join(required_deps['dependencies'])}")
            try:
                self.flutter_cli.pub_add(project_dir, required_deps['dependencies'])
                print("✅ Dependencies added successfully")
            except Exception as e:
                print(f"❌ Error adding dependencies: {e}")
                # Tenta adicionar uma por vez se falhar em batch
                self._install_individually(project_dir, required_deps['dependencies'], dev=False)

        # Instala dependências de desenvolvimento
        if required_deps['dev_dependencies']:
            print(f"Adding dev dependencies: {', '.join(required_deps['dev_dependencies'])}")
            try:
                self.flutter_cli.pub_add(project_dir, required_deps['dev_dependencies'], dev=True)
                print("✅ Dev dependencies added successfully")
            except Exception as e:
                print(f"❌ Error adding dev dependencies: {e}")
                # Tenta adicionar uma por vez se falhar em batch
                self._install_individually(project_dir, required_deps['dev_dependencies'], dev=True)

    def _install_individually(self, project_dir: str, packages: List[str], dev: bool = False):
        """
        Instala dependências uma por vez quando a instalação em batch falha.

        Args:
            project_dir (str): Diretório do projeto
            packages (List[str]): Lista de pacotes para instalar
            dev (bool): Se são dependências de desenvolvimento
        """
        successful = []
        failed = []

        for package in packages:
            try:
                print(f"  Adding {package}...")
                self.flutter_cli.pub_add(project_dir, [package], dev=dev)
                successful.append(package)
                print(f"  ✅ {package} added successfully")
            except Exception as e:
                print(f"  ❌ Failed to add {package}: {e}")
                failed.append(package)

        if successful:
            print(f"✅ Successfully installed: {', '.join(successful)}")
        if failed:
            print(f"❌ Failed to install: {', '.join(failed)}")
            print("You may need to add these dependencies manually.")

    def update_all_dependencies(self, project_dir: str):
        """
        Atualiza todas as dependências para as versões mais recentes.

        Args:
            project_dir (str): Diretório do projeto Flutter
        """
        print("Updating all dependencies...")
        try:
            self.flutter_cli.pub_upgrade(project_dir)
            print("✅ All dependencies updated successfully")
        except Exception as e:
            print(f"❌ Error updating dependencies: {e}")

    def remove_dependencies(self, project_dir: str, packages: List[str]):
        """
        Remove dependências específicas.

        Args:
            project_dir (str): Diretório do projeto
            packages (List[str]): Lista de pacotes para remover
        """
        if not packages:
            return

        print(f"Removing dependencies: {', '.join(packages)}")
        try:
            self.flutter_cli.pub_remove(project_dir, packages)
            print("✅ Dependencies removed successfully")
        except Exception as e:
            print(f"❌ Error removing dependencies: {e}")

    def get_dependency_tree(self, project_dir: str) -> str:
        """
        Obtém a árvore de dependências do projeto.

        Args:
            project_dir (str): Diretório do projeto

        Returns:
            str: Árvore de dependências
        """
        try:
            return self.flutter_cli.pub_deps(project_dir)
        except Exception as e:
            print(f"❌ Error getting dependency tree: {e}")
            return ""

    def verify_dependencies(self, project_dir: str) -> Dict[str, bool]:
        """
        Verifica se todas as dependências necessárias estão instaladas.

        Args:
            project_dir (str): Diretório do projeto

        Returns:
            Dict mapeando dependência -> está_instalada
        """
        required_deps = self.get_required_dependencies()
        all_required = required_deps['dependencies'] + required_deps['dev_dependencies']

        try:
            deps_output = self.flutter_cli.pub_deps(project_dir)
            installed_deps = self._parse_installed_dependencies(deps_output)

            verification = {}
            for dep in all_required:
                verification[dep] = dep in installed_deps

            return verification
        except Exception as e:
            print(f"❌ Error verifying dependencies: {e}")
            return {dep: False for dep in all_required}

    def _parse_installed_dependencies(self, deps_output: str) -> Set[str]:
        """
        Extrai os nomes das dependências instaladas da saída do pub deps.

        Args:
            deps_output (str): Saída do comando pub deps

        Returns:
            Set[str]: Conjunto de dependências instaladas
        """
        installed = set()

        for line in deps_output.split('\n'):
            line = line.strip()
            if line and not line.startswith('|') and not line.startswith('\\'):
                # Extrai o nome do pacote (primeira palavra antes do espaço)
                parts = line.split()
                if parts and not parts[0].startswith('-'):
                    package_name = parts[0].replace('├──', '').replace('└──', '').strip()
                    if package_name:
                        installed.add(package_name)

        return installed