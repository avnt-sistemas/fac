import re


class CaseConverter:
    def to_snake_case(self, text):
        """
        Convert a string to snake_case.

        Args:
            text (str): The string to convert.

        Returns:
            str: The converted string in snake_case.
        """
        # Remove special characters and replace spaces with underscores
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        text = text.strip().lower()
        text = re.sub(r'\s+', '_', text)

        # Ensure name doesn't start with a digit
        if text and text[0].isdigit():
            text = 'app_' + text

        return text

    def to_camel_case(self, text):
        """Convert text to camelCase"""
        components = text.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    def to_pascal_case(self, text):
        """Convert text to PascalCase"""
        components = text.split('_')
        return ''.join(x.title() for x in components)

    def to_kebab_case(self, text):
        """Convert text to kebab-case"""
        return self.to_snake_case(text).replace('_', '-')