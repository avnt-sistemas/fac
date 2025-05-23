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
        # First, handle the transition from lowercase to uppercase (camelCase/PascalCase)
        text = re.sub(r'([a-z])([A-Z])', r'\1_\2', text)
        # Handle multiple uppercase letters followed by lowercase (e.g., "XMLParser" -> "XML_Parser")
        text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', text)
        # Remove special characters
        text = re.sub(r'[^a-zA-Z0-9\s_]', '', text)
        # Replace spaces with underscores
        text = re.sub(r'\s+', '_', text)
        # Convert to lowercase
        text = text.lower()
        # Remove multiple underscores
        text = re.sub(r'_+', '_', text)
        # Remove leading/trailing underscores
        text = text.strip('_')

        # Ensure name doesn't start with a digit
        if text and text[0].isdigit():
            text = 'app_' + text

        return text

    def to_camel_case(self, text):
        """Convert text to camelCase"""
        # First convert to snake_case to normalize
        snake = self.to_snake_case(text)
        components = snake.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    def to_pascal_case(self, text):
        """Convert text to PascalCase"""
        # First convert to snake_case to normalize
        snake = self.to_snake_case(text)
        components = snake.split('_')
        return ''.join(x.title() for x in components)

    def to_kebab_case(self, text):
        """Convert text to kebab-case"""
        return self.to_snake_case(text).replace('_', '-')