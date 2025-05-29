import os
import re
import subprocess
import platform
import shutil
import yaml
from pathlib import Path
from typing import List, Dict, Optional


class FlutterCLI:
    def __init__(self, flutter_path=None):
        """
        Initialize the Flutter CLI wrapper.

        Args:
            flutter_path (str, optional): Path to the Flutter executable.
                If not provided, will try to find it in the PATH.
        """
        self.flutter_path = flutter_path

        if not self.flutter_path:
            # Try to find flutter in PATH
            self.flutter_path = self._find_flutter()

        if not self.flutter_path:
            raise FileNotFoundError(
                "Flutter executable not found. Please make sure Flutter is "
                "installed and in your PATH, or provide the path to the "
                "Flutter executable when initializing FlutterCLI."
            )

    def _find_flutter(self):
        """
        Find the Flutter executable in the PATH.

        Returns:
            str: Path to the Flutter executable, or None if not found.
        """
        # Check if 'flutter' command is available
        flutter_cmd = 'flutter.bat' if platform.system() == 'Windows' else 'flutter'
        flutter_path = shutil.which(flutter_cmd)

        if flutter_path:
            return flutter_path

        # Check common installation directories
        common_paths = []

        if platform.system() == 'Windows':
            # Windows common paths
            program_files = os.environ.get('ProgramFiles')
            program_files_x86 = os.environ.get('ProgramFiles(x86)')
            local_app_data = os.environ.get('LOCALAPPDATA')

            if program_files:
                common_paths.append(os.path.join(program_files, 'Flutter', 'bin', 'flutter.bat'))

            if program_files_x86:
                common_paths.append(os.path.join(program_files_x86, 'Flutter', 'bin', 'flutter.bat'))

            if local_app_data:
                common_paths.append(os.path.join(local_app_data, 'Flutter', 'bin', 'flutter.bat'))

        elif platform.system() == 'Darwin':
            # macOS common paths
            home = os.environ.get('HOME')
            if home:
                common_paths.append(os.path.join(home, 'flutter', 'bin', 'flutter'))
                common_paths.append(os.path.join(home, 'development', 'flutter', 'bin', 'flutter'))

        elif platform.system() == 'Linux':
            # Linux common paths
            home = os.environ.get('HOME')
            if home:
                common_paths.append(os.path.join(home, 'flutter', 'bin', 'flutter'))
                common_paths.append(os.path.join(home, 'development', 'flutter', 'bin', 'flutter'))

        # Check if any of the common paths exist
        for path in common_paths:
            if os.path.exists(path):
                return path

        return None

    def create_project(self, name, org, output_dir='.'):
        """
        Create a new Flutter project.

        Args:
            name (str): Name of the project.
            org (str): Organization domain name (e.g., com.example).
            output_dir (str, optional): Directory to create the project in. Default is current directory.
        """
        # Ensure the name is valid
        if not re.match(r'^[a-z][a-z0-9_]*$', name):
            raise ValueError(
                f"'{name}' is not a valid Dart package name. "
                "The name should consist of lowercase letters, numbers, and underscores, "
                "and should start with a letter."
            )

        cmd = [
            self.flutter_path,
            'create',
            '--org', org,
            '--project-name', name,
            os.path.join(output_dir, name)
        ]

        # print(f"Executing: {' '.join(cmd)}")

        try:
            subprocess.run(cmd, check=True)
            print(f"Successfully created Flutter project '{name}' in {output_dir}")
        except subprocess.CalledProcessError as e:
            print(f"Error creating Flutter project: {e}")
            raise
        except FileNotFoundError:
            print(f"Flutter executable not found at {self.flutter_path}")
            raise FileNotFoundError(
                "Flutter executable not found. Please make sure Flutter is "
                "installed and in your PATH, or provide the path to the "
                "Flutter executable when initializing FlutterCLI."
            )

    def pub_add(self, project_dir: str, packages: List[str], dev: bool = False):
        """
        Add packages using 'flutter pub add'.

        Args:
            project_dir (str): Path to the Flutter project directory.
            packages (List[str]): List of package names to add.
            dev (bool, optional): Add as dev dependencies. Default is False.
        """
        if not packages:
            return

        cmd = [self.flutter_path, 'pub', 'add']

        if dev:
            cmd.append('--dev')

        cmd.extend(packages)

        # print(f"Executing: {' '.join(cmd)} in {project_dir}")

        try:
            result = subprocess.run(cmd, cwd=project_dir, check=True,
                                    capture_output=True, text=True)
            # print(f"Successfully added packages: {', '.join(packages)}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error adding packages {packages}: {e}")
            if e.stdout:
                print(f"stdout: {e.stdout}")
            if e.stderr:
                print(f"stderr: {e.stderr}")
            raise

    def pub_remove(self, project_dir: str, packages: List[str]):
        """
        Remove packages using 'flutter pub remove'.

        Args:
            project_dir (str): Path to the Flutter project directory.
            packages (List[str]): List of package names to remove.
        """
        if not packages:
            return

        cmd = [self.flutter_path, 'pub', 'remove'] + packages

        # print(f"Executing: {' '.join(cmd)} in {project_dir}")

        try:
            result = subprocess.run(cmd, cwd=project_dir, check=True,
                                    capture_output=True, text=True)
            print(f"Successfully removed packages: {', '.join(packages)}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error removing packages {packages}: {e}")
            raise

    def pub_get(self, project_dir: str):
        """
        Run 'flutter pub get' in the specified project directory.

        Args:
            project_dir (str): Path to the Flutter project directory.
        """
        cmd = [self.flutter_path, 'pub', 'get']

        # print(f"Executing: {' '.join(cmd)} in {project_dir}")

        try:
            result = subprocess.run(cmd, cwd=project_dir, check=True,
                                    capture_output=True, text=True)
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error running 'flutter pub get': {e}")
            if e.stderr:
                print(f"stderr: {e.stderr}")
            raise

    def pub_upgrade(self, project_dir: str, packages: Optional[List[str]] = None):
        """
        Upgrade packages using 'flutter pub upgrade'.

        Args:
            project_dir (str): Path to the Flutter project directory.
            packages (List[str], optional): List of specific packages to upgrade.
                If None, upgrades all packages.
        """
        cmd = [self.flutter_path, 'pub', 'upgrade']

        if packages:
            cmd.extend(packages)

        # print(f"Executing: {' '.join(cmd)} in {project_dir}")

        try:
            result = subprocess.run(cmd, cwd=project_dir, check=True,
                                    capture_output=True, text=True)
            print("Successfully upgraded packages")
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error upgrading packages: {e}")
            raise

    def pub_deps(self, project_dir: str, normalize_output: bool = True):
        """
        Show dependency tree using 'flutter pub deps'.

        Args:
            project_dir (str): Path to the Flutter project directory.
            normalize_output (bool): Se True, normaliza os caracteres Unicode para ASCII.

        Returns:
            str: Saída do comando pub deps
        """
        cmd = [self.flutter_path, 'pub', 'deps']

        try:
            # Configurar environment para forçar saída ASCII no Windows
            env = os.environ.copy()
            if platform.system() == 'Windows':
                # Forçar codificação UTF-8
                env['PYTHONIOENCODING'] = 'utf-8'
                env['CHCP'] = '65001'  # UTF-8 code page

            result = subprocess.run(
                cmd,
                cwd=project_dir,
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                env=env
            )

            output = result.stdout

            if normalize_output:
                output = self._normalize_tree_chars(output)

            return output

        except subprocess.CalledProcessError as e:
            print(f"Error getting dependencies: {e}")
            if e.stderr:
                print(f"stderr: {e.stderr}")
            raise

    def _normalize_tree_chars(self, text: str) -> str:
        """
        Normaliza os caracteres Unicode de desenho de árvore para ASCII.

        Args:
            text (str): Texto com caracteres Unicode

        Returns:
            str: Texto com caracteres ASCII normalizados
        """
        # Mapeamento de caracteres Unicode para ASCII
        unicode_to_ascii = {
            # Caracteres de caixa Unicode -> ASCII equivalentes
            '├': '|',
            '│': '|',
            '└': '`',
            '─': '-',
            '├──': '|--',
            '└──': '`--',
            '│   ': '|   ',
            # Outros possíveis caracteres
            '┌': '+',
            '┐': '+',
            '┘': '+',
            '┴': '+',
            '┼': '+',
            '┤': '+',
        }

        # Substituir caracteres Unicode pelos equivalentes ASCII
        for unicode_char, ascii_char in unicode_to_ascii.items():
            text = text.replace(unicode_char, ascii_char)

        # Padrões mais complexos para árvores
        # Substituir padrões comuns de árvore Unicode
        patterns = [
            (r'├──\s*', '|-- '),
            (r'└──\s*', '`-- '),
            (r'│\s{2,}', '|   '),
            (r'├─', '|-'),
            (r'└─', '`-'),
        ]

        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)

        return text

    def get_pubspec(self, project_dir: str):
        """
        Recupera o conteúdo do arquivo pubspec.yaml de um projeto Flutter.

        Args:
            project_dir (str): Caminho para o diretório do projeto Flutter

        Returns:
            dict: Conteúdo do pubspec.yaml como dicionário

        Raises:
            FileNotFoundError: Se o arquivo pubspec.yaml não for encontrado
            yaml.YAMLError: Se houver erro ao fazer parse do YAML
        """
        # Construir o caminho para o pubspec.yaml
        pubspec_path = Path(project_dir) / 'pubspec.yaml'

        # Verificar se o arquivo existe
        if not pubspec_path.exists():
            raise FileNotFoundError(f"pubspec.yaml não encontrado em: {pubspec_path}")

        try:
            # Ler e fazer parse do arquivo YAML
            with open(pubspec_path, 'r', encoding='utf-8') as file:
                pubspec_content = yaml.safe_load(file)

            return pubspec_content

        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Erro ao fazer parse do pubspec.yaml: {e}")
        except Exception as e:
            raise Exception(f"Erro ao ler pubspec.yaml: {e}")

    def pub_genl10n(self, project_dir: str):
        """
        Run 'flutter pub gen-l10n' command.
        """
        cmd = [self.flutter_path, 'gen-l10n']

        # print(f"Executing: {' '.join(cmd)} in {project_dir}")

        try:
            result = subprocess.run(cmd, cwd=project_dir, check=True,
                                    capture_output=True, text=True)
            # print("Successfully generated l10n files")
            return result
        except subprocess.CalledProcessError as e:
            if e.stdout:
                print(f"stdout: {e.stdout}")
            if e.stderr:
                print(f"stderr: {e.stderr}")
            raise

    def verify_dependencies(self, project_dir: str) -> Dict:
        """
        Verifica e analisa as dependências do projeto.

        Args:
            project_dir (str): Path to the Flutter project directory.

        Returns:
            Dict: Análise das dependências
        """
        try:
            # Obter saída das dependências
            deps_output = self.pub_deps(project_dir, normalize_output=True)

            # Análise básica
            analysis = {
                'raw_output': deps_output,
                'total_packages': 0,
                'flutter_version': None,
                'dart_version': None,
                'packages': []
            }

            # Extrair informações básicas
            lines = deps_output.split('\n')
            package_count = 0

            for line in lines:
                if 'Dart SDK' in line:
                    analysis['dart_version'] = line.strip()
                elif 'Flutter SDK' in line:
                    analysis['flutter_version'] = line.strip()
                elif line.strip() and not line.startswith('Dart SDK') and not line.startswith('Flutter SDK'):
                    # Contar linhas que parecem ser pacotes
                    if re.match(r'[|`\s]*[a-zA-Z0-9_]+\s+[0-9]+\.[0-9]+\.[0-9]+', line):
                        package_count += 1
                        # Extrair nome do pacote
                        match = re.search(r'([a-zA-Z0-9_]+)\s+([0-9]+\.[0-9]+\.[0-9]+[^\s]*)', line)
                        if match:
                            analysis['packages'].append({
                                'name': match.group(1),
                                'version': match.group(2)
                            })

            analysis['total_packages'] = len(analysis['packages'])

            return analysis

        except Exception as e:
            print(f"Error verifying dependencies: {e}")
            return {
                'error': str(e),
                'raw_output': None,
                'total_packages': 0,
                'packages': []
            }

    # Método legado para compatibilidade
    def run_pub_get(self, project_dir):
        """Legacy method for compatibility."""
        return self.pub_get(project_dir)

    def list_methods(self):
        """
        Lista todos os métodos disponíveis na classe.
        Útil para debug quando um método não é encontrado.
        """
        methods = [method for method in dir(self) if not method.startswith('_')]
        print("Métodos disponíveis na classe FlutterCLI:")
        for method in sorted(methods):
            print(f"  - {method}")
        return methods


# Exemplo de uso e teste
if __name__ == "__main__":
    try:
        # Instanciar a classe
        flutter_cli = FlutterCLI()

        print("Flutter CLI inicializado com sucesso!")
        print(f"Caminho do Flutter: {flutter_cli.flutter_path}")

        # Listar métodos disponíveis
        flutter_cli.list_methods()

        # Teste básico de criação de projeto (descomente para testar)
        # flutter_cli.create_project("test_app", "com.example", ".")

    except FileNotFoundError as e:
        print(f"Erro: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")