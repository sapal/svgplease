import unittest

import svgplease
import svgplease.parse

class ParseFilename(unittest.TestCase):
    def tokens(self, tokens):
        return svgplease.parse.join_tokens(tokens)

    def parse(self, class_name, *tokens):
        return getattr(svgplease.parse, class_name).parser().parse_text(self.tokens(tokens), eof=True)

    def test_parse_normal_filename(self):
        self.assertEqual(self.parse("Filename", "file.svg").filename, "file.svg")

    def test_parse_filename_with_whitespace(self):
        self.assertEqual(self.parse("Filename", "file name.svg").filename, "file name.svg")

    def test_parse_special_filename(self):
        self.assertRaises(svgplease.parse.ParseError, self.parse, "Filename", "then")
        self.assertRaises(svgplease.parse.ParseError, self.parse, "Filename", "file")

    def test_parse_prefixed_filename(self):
        self.assertEqual(self.parse("Filename", "file", "file.svg").filename, "file.svg")

