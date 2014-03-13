import unittest

import svgplease
import svgplease.parse

class TestParse(unittest.TestCase):
    """Base class for Parse* tests."""
    tested_class_name = None
    def tokens(self, tokens):
        return svgplease.parse.join_tokens(tokens)

    def parse(self, *tokens):
        return getattr(svgplease.parse, self.tested_class_name).parser().parse_text(
                self.tokens(tokens), eof=True)

    def assertParsingFailed(self, *tokens):
        self.assertRaises(svgplease.parse.ParseError, self.parse, *tokens)

class ParseFilename(TestParse):
    tested_class_name = "Filename"

    def test_parse_normal_filename(self):
        self.assertEqual(self.parse("file.svg").filename, "file.svg")

    def test_parse_filename_with_whitespace(self):
        self.assertEqual(self.parse("file name.svg").filename, "file name.svg")

    def test_parse_special_filename(self):
        self.assertParsingFailed("then")
        self.assertParsingFailed("file")

    def test_parse_prefixed_filename(self):
        self.assertEqual(self.parse("file", "file.svg").filename, "file.svg")


