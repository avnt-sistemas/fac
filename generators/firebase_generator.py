import os
import re
import json
import subprocess
from typing import Optional, Dict, List
from jinja2 import Environment, FileSystemLoader


class FirebaseGenerator:
    def __init__(self, app_dir: str, config: Dict, dependency_manager=None):
        self.app_dir = app_dir
        self.config = config
        self.dependency_manager = dependency_manager

        # Set up Jinja2 environment
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def setup_firebase(self):
        """Setup Firebase for the Flutter app"""
        print("🔥 Setting up Firebase...")

        # Get Firebase project ID
        firebase_app_id = self._get_firebase_app_id()
        print(f"Firebase app ID: {firebase_app_id}")

        # Check if Flutter Fire CLI is installed
        self._ensure_flutterfire_cli()

        # Check if Firebase CLI is installed
        self._ensure_firebase_cli()

        # Login to Firebase (if needed)
        self._ensure_firebase_login()

        # Create or verify Firebase project
        project_id = self._ensure_firebase_project(firebase_app_id)

        # Configure Firebase for Flutter
        self._configure_firebase_for_flutter(project_id)

        # Add Firebase dependencies using DependencyManager
        if self.dependency_manager:
            self._add_firebase_dependencies()

        print("✅ Firebase setup completed successfully!")

    def _get_firebase_app_id(self) -> str:
        """
        Get Firebase app ID from config or derive from package name.

        Returns:
            str: Firebase app ID
        """
        # Check if firebase_app is specified in config
        if 'firebase_app' in self.config.get('app', {}):
            return self.config['app']['firebase_app']

        # Extract from package name (everything after last dot)
        package_name = self.config.get('app', {}).get('package', '')
        if '.' in package_name:
            return package_name.split('.')[-1]

        # Fallback to app name
        app_name = self.config.get('app', {}).get('name', 'flutter-app')
        # Convert to Firebase-friendly format
        return re.sub(r'[^a-z0-9-]', '-', app_name.lower())

    def _ensure_flutterfire_cli(self):
        """Ensure FlutterFire CLI is installed"""
        try:
            result = subprocess.run(['flutterfire', '--version'],
                                    check=True, capture_output=True, text=True)
            print(f"✅ FlutterFire CLI is installed: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("📦 Installing FlutterFire CLI...")
            try:
                subprocess.run(['dart', 'pub', 'global', 'activate', 'flutterfire_cli'],
                               check=True)
                print("✅ FlutterFire CLI installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install FlutterFire CLI: {e}")
                raise

    def _ensure_firebase_cli(self):
        """Ensure Firebase CLI is installed"""
        try:
            result = subprocess.run(['firebase', '--version'],
                                    check=True, capture_output=True, text=True)
            print(f"✅ Firebase CLI is available: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Firebase CLI not found!")
            print("Please install Firebase CLI:")
            print("  npm install -g firebase-tools")
            print("  or visit: https://firebase.google.com/docs/cli#install_the_firebase_cli")
            raise FileNotFoundError("Firebase CLI is required but not installed")

    def _ensure_firebase_login(self):
        """Ensure user is logged in to Firebase"""
        try:
            result = subprocess.run(['firebase', 'projects:list'],
                                    check=True, capture_output=True, text=True)
            print("✅ Firebase authentication verified")
            return True
        except subprocess.CalledProcessError:
            print("🔐 Firebase login required...")
            try:
                subprocess.run(['firebase', 'login'], check=True)
                print("✅ Firebase login successful")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Firebase login failed: {e}")
                print("Please run 'firebase login' manually and try again")
                raise

    def _get_firebase_projects(self) -> List[Dict]:
        """Get list of Firebase projects"""
        try:
            result = subprocess.run(['firebase', 'projects:list', '--json'],
                                    check=True, capture_output=True, text=True)
            projects_data = json.loads(result.stdout)
            return projects_data
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"❌ Failed to get Firebase projects: {e}")
            return []

    def _project_exists(self, project_id: str) -> bool:
        """Check if Firebase project exists"""
        projects = self._get_firebase_projects()

        for project in projects:
            if (project.get('projectId') == project_id or
                    project.get('displayName', '').lower() == project_id.lower()):
                return True

        return False

    def _create_firebase_project(self, project_id: str) -> str:
        """
        Create a new Firebase project.

        Args:
            project_id (str): Desired project ID

        Returns:
            str: Actual project ID created
        """
        print(f"🏗️ Creating Firebase project: {project_id}")

        try:
            # Firebase project IDs have specific requirements
            safe_project_id = self._make_safe_project_id(project_id)

            # Create the project
            cmd = ['firebase', 'projects:create', safe_project_id,
                   '--display-name', project_id.replace('-', ' ').title()]

            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

            print(f"✅ Firebase project created: {safe_project_id}")
            return safe_project_id

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create Firebase project: {e}")
            if "already exists" in str(e.stderr):
                print(f"Project {safe_project_id} already exists, using it.")
                return safe_project_id
            raise

    def _make_safe_project_id(self, project_id: str) -> str:
        """
        Make project ID safe for Firebase.

        Firebase project IDs must:
        - Be 6-30 characters
        - Contain only lowercase letters, numbers, and hyphens
        - Start with a letter
        - Not end with a hyphen
        """
        # Convert to lowercase and replace invalid chars with hyphens
        safe_id = re.sub(r'[^a-z0-9-]', '-', project_id.lower())

        # Ensure it starts with a letter
        if not safe_id[0].isalpha():
            safe_id = 'app-' + safe_id

        # Remove trailing hyphens
        safe_id = safe_id.rstrip('-')

        # Ensure length constraints
        if len(safe_id) < 6:
            safe_id = safe_id + '-app'
        elif len(safe_id) > 30:
            safe_id = safe_id[:30].rstrip('-')

        return safe_id

    def _ensure_firebase_project(self, firebase_app_id: str) -> str:
        """
        Ensure Firebase project exists, create if it doesn't.

        Args:
            firebase_app_id (str): Desired Firebase app ID

        Returns:
            str: Actual Firebase project ID
        """
        # Check if project exists
        if self._project_exists(firebase_app_id):
            print(f"✅ Firebase project '{firebase_app_id}' already exists")
            return firebase_app_id

        # Try to create the project
        try:
            return self._create_firebase_project(firebase_app_id)
        except Exception as e:
            print(f"❌ Could not create Firebase project: {e}")

            # List available projects for user to choose from
            projects = self._get_firebase_projects()
            if projects:
                print("Available Firebase projects:")
                for i, project in enumerate(projects):
                    print(f"  {i + 1}. {project.get('projectId')} - {project.get('displayName', 'No name')}")

                # For now, return the first available project
                # In a real scenario, you might want to prompt the user
                selected_project = projects[0]['projectId']
                print(f"🔄 Using existing project: {selected_project}")
                return selected_project
            else:
                raise Exception("No Firebase projects available and could not create new one")

    def _configure_firebase_for_flutter(self, project_id: str):
        """Configure Firebase for Flutter using FlutterFire CLI"""
        print(f"⚙️ Configuring Firebase for Flutter project: {project_id}")

        # Determine platforms to configure
        platforms = self._get_target_platforms()
        platforms_str = ','.join(platforms)

        try:
            cmd = [
                'flutterfire', 'configure',
                '--project', project_id,
                '--out', 'lib/firebase_options.dart',
                '--platforms', platforms_str,
                '--yes'  # Auto-confirm prompts
            ]

            print(f"Running: {' '.join(cmd)}")

            result = subprocess.run(cmd, cwd=self.app_dir, check=True,
                                    capture_output=True, text=True)

            print("✅ Firebase configuration completed")
            print(f"📄 firebase_options.dart generated successfully")

            # Verify the file was created
            firebase_options_path = os.path.join(self.app_dir, 'lib', 'firebase_options.dart')
            if os.path.exists(firebase_options_path):
                print(f"✅ Verified: {firebase_options_path} exists")
            else:
                print(f"⚠️ Warning: {firebase_options_path} was not created")
                self._generate_placeholder_firebase_options()

        except subprocess.CalledProcessError as e:
            print(f"❌ Firebase configuration failed: {e}")
            print(f"stderr: {e.stderr}")
            print("🔄 Generating placeholder firebase_options.dart")
            self._generate_placeholder_firebase_options()

    def _get_target_platforms(self) -> List[str]:
        """Get target platforms for Firebase configuration"""
        # You can make this configurable in the future
        default_platforms = ['android', 'ios', 'web']

        # Check if specific platforms are configured
        platforms = self.config.get('firebase', {}).get('platforms', default_platforms)

        return platforms

    def _generate_placeholder_firebase_options(self):
        """Generate placeholder firebase_options.dart file"""
        try:
            template = self.jinja_env.get_template('firebase/firebase_options.dart.jinja')
            output = template.render(
                project_id=self._get_firebase_app_id(),
                app_name=self.config.get('app', {}).get('name', 'Flutter App')
            )

            firebase_options_path = os.path.join(self.app_dir, 'lib', 'firebase_options.dart')
            os.makedirs(os.path.dirname(firebase_options_path), exist_ok=True)

            with open(firebase_options_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(output)

            print("📄 Placeholder firebase_options.dart generated")
            print("⚠️ Please run 'flutterfire configure' manually to set up real Firebase configuration")

        except Exception as e:
            print(f"❌ Failed to generate placeholder firebase_options.dart: {e}")

    def _add_firebase_dependencies(self):
        """Add Firebase dependencies using DependencyManager"""
        if not self.dependency_manager:
            print("⚠️ DependencyManager not available, skipping Firebase dependency installation")
            return

        print("📦 Adding Firebase dependencies...")

        firebase_packages = []

        # Always add core Firebase
        firebase_packages.append('firebase_core')

        # Add auth if enabled
        if self.config.get('auth', {}).get('enabled', False):
            firebase_packages.extend(['firebase_auth'])

            # Add Google Sign In if configured
            auth_providers = self.config.get('auth', {}).get('providers', [])
            if 'google' in auth_providers:
                firebase_packages.append('google_sign_in')

        # Add Firestore if using Firebase persistence
        if self.config.get('persistence', {}).get('provider') == 'firebase':
            firebase_packages.append('cloud_firestore')

        # Add Storage if configured
        if self.config.get('firebase', {}).get('storage', True):
            firebase_packages.append('firebase_storage')

        # Add Analytics if configured
        if self.config.get('firebase', {}).get('analytics', True):
            firebase_packages.append('firebase_analytics')

        # Install the packages
        try:
            # Use the dependency manager's flutter_cli to add packages
            self.dependency_manager.flutter_cli.pub_add(self.app_dir, firebase_packages)
            print(f"✅ Firebase dependencies added: {', '.join(firebase_packages)}")
        except Exception as e:
            print(f"❌ Failed to add Firebase dependencies: {e}")
            print("You may need to add them manually:")
            for package in firebase_packages:
                print(f"  flutter pub add {package}")

    def enable_firebase_service(self, service: str, project_id: str):
        """
        Enable specific Firebase service for the project.

        Args:
            service (str): Service to enable (e.g., 'firestore', 'auth', 'storage')
            project_id (str): Firebase project ID
        """
        service_commands = {
            'auth': ['firebase', 'projects:list'],  # Auth is usually enabled by default
            'firestore': ['firebase', 'firestore:enable', '--project', project_id],
            'storage': ['firebase', 'storage:rules:create', '--project', project_id],
            'analytics': ['firebase', 'analytics:enable', '--project', project_id]
        }

        if service not in service_commands:
            print(f"⚠️ Unknown Firebase service: {service}")
            return

        try:
            print(f"🔧 Enabling Firebase {service}...")
            subprocess.run(service_commands[service], check=True, capture_output=True)
            print(f"✅ Firebase {service} enabled")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Could not enable Firebase {service}: {e}")
            print(f"Please enable it manually in the Firebase Console")

    def setup_firebase_services(self, project_id: str):
        """Setup required Firebase services based on configuration"""
        services_to_enable = []

        # Check what services are needed based on config
        if self.config.get('auth', {}).get('enabled', False):
            services_to_enable.append('auth')

        if self.config.get('persistence', {}).get('provider') == 'firebase':
            services_to_enable.append('firestore')

        if self.config.get('firebase', {}).get('storage', True):
            services_to_enable.append('storage')

        if self.config.get('firebase', {}).get('analytics', True):
            services_to_enable.append('analytics')

        # Enable each service
        for service in services_to_enable:
            self.enable_firebase_service(service, project_id)

    def get_firebase_config_info(self) -> Dict:
        """Get Firebase configuration information"""
        firebase_options_path = os.path.join(self.app_dir, 'lib', 'firebase_options.dart')

        info = {
            'firebase_options_exists': os.path.exists(firebase_options_path),
            'firebase_options_path': firebase_options_path,
            'project_id': self._get_firebase_app_id(),
            'configured_platforms': self._get_target_platforms()
        }

        return info