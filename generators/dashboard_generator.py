import os
from jinja2 import Environment, FileSystemLoader


class DashboardGenerator:
    def __init__(self, app_dir, config):
        self.app_dir = app_dir
        self.config = config

        # Set up Jinja2 environment
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def generate(self):
        """Generate dashboard files for the Flutter app"""
        # Check if dashboard is enabled in config
        if not self.config.get('dashboard', {}).get('enabled', False):
            return

        # Create dashboard directories
        dashboard_dir = os.path.join(self.app_dir, 'lib', 'features', 'dashboard')
        os.makedirs(os.path.join(dashboard_dir, 'presentation', 'screens'), exist_ok=True)
        os.makedirs(os.path.join(dashboard_dir, 'presentation', 'widgets'), exist_ok=True)

        # Get dashboard widgets from config
        widgets = self.config.get('dashboard', {}).get('widgets', [])

        # Generate dashboard screen
        self._generate_dashboard_screen(dashboard_dir, widgets)

        # Generate chart widgets
        for widget in widgets:
            if widget.get('type') == 'bar_chart':
                self._generate_bar_chart_widget(dashboard_dir, widget)
            elif widget.get('type') == 'pie_chart':
                self._generate_pie_chart_widget(dashboard_dir, widget)
            elif widget.get('type') == 'line_chart':
                self._generate_line_chart_widget(dashboard_dir, widget)
            elif widget.get('type') == 'kpi':
                self._generate_kpi_widget(dashboard_dir, widget)

    def _generate_dashboard_screen(self, dashboard_dir, widgets):
        """Generate the main dashboard screen"""
        template = self.jinja_env.get_template('dashboard/dashboard_screen.dart.jinja')
        output = template.render(
            widgets=widgets,
            has_bar_chart=any(w.get('type') == 'bar_chart' for w in widgets),
            has_pie_chart=any(w.get('type') == 'pie_chart' for w in widgets),
            has_line_chart=any(w.get('type') == 'line_chart' for w in widgets),
            has_kpi=any(w.get('type') == 'kpi' for w in widgets),
        )

        output_path = os.path.join(dashboard_dir, 'presentation', 'screens', 'dashboard_screen.dart')
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(output)

    def _generate_bar_chart_widget(self, dashboard_dir, widget_config):
        """Generate a bar chart widget"""
        template = self.jinja_env.get_template('dashboard/bar_chart_widget.dart.jinja')
        output = template.render(
            widget_config=widget_config,
        )

        output_path = os.path.join(dashboard_dir, 'presentation', 'widgets', 'bar_chart_widget.dart')
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(output)

    def _generate_pie_chart_widget(self, dashboard_dir, widget_config):
        """Generate a pie chart widget"""
        template = self.jinja_env.get_template('dashboard/pie_chart_widget.dart.jinja')
        output = template.render(
            widget_config=widget_config,
        )

        output_path = os.path.join(dashboard_dir, 'presentation', 'widgets', 'pie_chart_widget.dart')
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(output)

    def _generate_line_chart_widget(self, dashboard_dir, widget_config):
        """Generate a line chart widget"""
        template = self.jinja_env.get_template('dashboard/line_chart_widget.dart.jinja')
        output = template.render(
            widget_config=widget_config,
        )

        output_path = os.path.join(dashboard_dir, 'presentation', 'widgets', 'line_chart_widget.dart')
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(output)

    def _generate_kpi_widget(self, dashboard_dir, widget_config):
        """Generate a KPI widget"""
        template = self.jinja_env.get_template('dashboard/kpi_widget.dart.jinja')
        output = template.render(
            widget_config=widget_config,
        )

        output_path = os.path.join(dashboard_dir, 'presentation', 'widgets', 'kpi_widget.dart')
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(output)