import unittest
from helpers import get_language_code, get_language_name


class TestLanguageMappings(unittest.TestCase):
    def test_get_language_code(self):
        self.assertEqual(get_language_code("English"), "en")
        self.assertEqual(get_language_code("english"), "en")  # Case-insensitive
        self.assertEqual(get_language_code("Russian"), "ru")
        self.assertEqual(get_language_code("russian"), "ru")
        self.assertEqual(get_language_code("Indonesian"), "id")
        self.assertEqual(get_language_code("unknown"), "en")  # Default

    def test_get_language_name(self):
        self.assertEqual(get_language_name("en"), "English")
        self.assertEqual(get_language_name("EN"), "English")  # Case-insensitive
        self.assertEqual(get_language_name("ru"), "Russian")
        self.assertEqual(get_language_name("RU"), "Russian")
        self.assertEqual(get_language_name("id"), "Indonesian")
        self.assertEqual(get_language_name("unknown"), "English")  # Default

# if __name__ == "__main__":
#     unittest.main()
