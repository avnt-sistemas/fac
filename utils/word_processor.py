import inflect
from inflector import Inflector


class WordProcessor:
    def __init__(self, language='en'):
        """
        Initialize the WordInflector with a specific language.
        Args:
            language (str): Language code ('en' for English, 'pt' for Portuguese).
        """
        self.language = language

        # Initialize inflection engines based on language
        if language == 'en':
            self.engine = inflect.engine()
        elif language == 'pt':
            self.engine = Inflector('pt')
        else:
            self.engine = None

    def pluralize(self, word):
        """
        Convert a word to its plural form.
        Args:
            word (str): The word to pluralize.
        Returns:
            str: The pluralized word.
        """
        if self.language == 'en':
            return self.engine.plural(word)
        elif self.language == 'pt':
            return self.engine.pluralize(word)
        else:
            return word

    def singularize(self, word):
        """
        Convert a word to its singular form.
        Args:
            word (str): The word to singularize.
        Returns:
            str: The singular form of the word.
        """
        if self.language == 'en':
            singular = self.engine.singular_noun(word)
            return singular if singular else word
        elif self.language == 'pt':
            return self.engine.singularize(word)
        else:
            return word

    def is_plural(self, word):
        """
        Check if a word is in plural form.
        Args:
            word (str): The word to check.
        Returns:
            bool: True if the word is plural, False otherwise.
        """
        if self.language == 'en':
            singular = self.engine.singular_noun(word)
            return bool(singular)
        elif self.language == 'pt':
            return word != self.engine.singularize(word)
        else:
            return False

    def plural_verb(self, verb, count):
        """
        Return the plural or singular form of a verb based on count.
        Only available for English.
        Args:
            verb (str): The verb to pluralize/singularize.
            count (int): The count determining which form to use.
        Returns:
            str: The appropriate form of the verb.
        """
        if self.language == 'en':
            return self.engine.plural_verb(verb, count)
        else:
            return verb

    def plural_adj(self, adj, count):
        """
        Return the plural or singular form of an adjective based on count.
        Only available for English.
        Args:
            adj (str): The adjective to pluralize/singularize.
            count (int): The count determining which form to use.
        Returns:
            str: The appropriate form of the adjective.
        """
        if self.language == 'en':
            return self.engine.plural_adj(adj, count)
        else:
            return adj

    def plural_noun(self, noun, count):
        """
        Return the plural or singular form of a noun based on count.
        Args:
            noun (str): The noun to pluralize/singularize.
            count (int): The count determining which form to use.
        Returns:
            str: The appropriate form of the noun.
        """
        if count == 1:
            return self.singularize(noun)
        else:
            return self.pluralize(noun)