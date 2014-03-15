import unittest

import svgplease
import svgplease.parse
from svgplease import command

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
        self.assertParsingFailed("to")

    def test_parse_prefixed_filename(self):
        self.assertEqual(self.parse("file", "file.svg").filename, "file.svg")

class ParseOpen(TestParse):
    tested_class_name = "Open"

    def test_open_single_file(self):
        self.assertEqual(self.parse("open", "file.svg").command, command.Open("file.svg"))

    def test_open_multiple_files(self):
        self.assertEqual(self.parse("open", "file.svg", "other file.svg", "file", "then").command,
                command.Open("file.svg", "other file.svg", "then"))

class ParseSave(TestParse):
    tested_class_name = "Save"

    def test_save_single_file(self):
        self.assertEqual(self.parse("save", "file.svg").command, command.Save("file.svg"))

    def test_save_to_files(self):
        self.assertEqual(self.parse("save", "to", "file1.svg", "file2.svg").command,
                command.Save("file1.svg", "file2.svg"))

class ParseCommandList(TestParse):
    tested_class_name = "CommandList"

    def test_open_command(self):
        self.assertEqual(self.parse("open", "file.svg").command_list, [command.Open("file.svg")])

    def test_save_command(self):
        self.assertEqual(self.parse("save", "to", "file2.svg").command_list, [command.Save("file2.svg")])

    def test_two_commands(self):
        self.assertEqual(
                self.parse("open", "file.svg", "then", "save", "to", "file1.svg").command_list,
                [command.Open("file.svg"), command.Save("file1.svg")])

class ParseNumber(TestParse):
    tested_class_name = "Number"

    def test_integer(self):
        self.assertEqual(self.parse("12").number, 12.0)

    def test_float(self):
        self.assertEqual(self.parse("10.52").number, 10.52)

    def test_positive(self):
        self.assertEqual(self.parse("+3").number, 3.0)

    def test_negative(self):
        self.assertEqual(self.parse("-5.5").number, -5.5)

class ParseColor(TestParse):
    tested_class_name = "Color"

    def test_hash_rgb(self):
        self.assertEqual(str(self.parse("#00ff0a").color), "#00ff0a")

    def test_hash_rgba(self):
        self.assertEqual(self.parse("#0f88ff80").color.alpha, 128)

    def test_value_rgb(self):
        self.assertEqual(self.parse("rgb(10, 219,255)").color.rgb, (10, 219, 255))
        self.assertEqual(self.parse("rgb( 00, 003, 1)").color.rgb, (0, 3, 1))

