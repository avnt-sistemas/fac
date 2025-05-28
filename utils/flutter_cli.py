import os
import re
import subprocess
import platform
import shutil
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

        print(f"Executing: {' '.join(cmd)}")

        try:
            subprocess.run(cmd, check=True)
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

        print(f"Executing: {' '.join(cmd)} in {project_dir}")

        try:
            result = subprocess.run(cmd, cwd=project_dir, check=True,
                                    capture_output=True, text=True)
            print(f"Successfully added packages: {', '.join(packages)}")
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

        print(f"Executing: {' '.join(cmd)} in {project_dir}")

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

        print(f"Executing: {' '.join(cmd)} in {project_dir}")

        try:
            subprocess.run(cmd, cwd=project_dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running 'flutter pub get': {e}")
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

        print(f"Executing: {' '.join(cmd)} in {project_dir}")

        try:
            result = subprocess.run(cmd, cwd=project_dir, check=True,
                                    capture_output=True, text=True)
            print("Successfully upgraded packages")
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error upgrading packages: {e}")
            raise

    def pub_deps(self, project_dir: str):
        """
        Show dependency tree using 'flutter pub deps'.

        Args:
            project_dir (str): Path to the Flutter project directory.
        """
        cmd = [self.flutter_path, 'pub', 'deps']

        try:
            result = subprocess.run(cmd, cwd=project_dir, check=True,
                                    capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error getting dependencies: {e}")
            raise

    # Método legado para compatibilidade
    def run_pub_get(self, project_dir):
        """Legacy method for compatibility."""
        return self.pub_get(project_dir)