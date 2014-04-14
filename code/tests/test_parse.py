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
                self.tokens(tokens), eof=True, matchtype="complete")

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

    def test_change_color_command(self):
        self.assertEqual(self.parse("change", "color", "to", "#ffffff").command_list,
                [command.ChangeColor(fill_stroke=command.FillStroke(), to_color=command.Color(255, 255, 255))])
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

class ParseFillStroke(TestParse):
    tested_class_name = "FillStroke"

    def test_default(self):
        self.assertEqual(self.parse().fill_stroke, command.FillStroke())

    def test_fill_stroke(self):
        self.assertEqual(self.parse("fill", "stroke").fill_stroke, command.FillStroke())
        self.assertEqual(self.parse("fill", "and", "stroke").fill_stroke, command.FillStroke())
        self.assertEqual(self.parse("stroke", "fill").fill_stroke, command.FillStroke())
        self.assertEqual(self.parse("stroke", "and", "fill").fill_stroke, command.FillStroke())

    def test_fill_or_stroke(self):
        self.assertEqual(self.parse("fill").fill_stroke, command.FillStroke(fill=True))
        self.assertEqual(self.parse("stroke").fill_stroke, command.FillStroke(stroke=True))

class ParseChangeColor(TestParse):
    tested_class_name = "ChangeColor"

    def test_fill_color(self):
        self.assertEqual(self.parse("change", "fill", "color", "to", "#ff0000").command,
                         command.ChangeColor(fill_stroke=command.FillStroke(fill=True),
                                             to_color=command.Color(255, 0, 0)))

    def test_fill_stroke_color(self):
        self.assertEqual(self.parse("change", "color", "#00ff00ff").command,
                         command.ChangeColor(fill_stroke=command.FillStroke(),
                                             to_color=command.Color(0, 255, 0, 255)))

    def test_from_color(self):
        self.assertEqual(self.parse("change", "stroke", "color", "from", "rgb(10, 10, 10)", "to", "#ffffff").command,
                         command.ChangeColor(fill_stroke=command.FillStroke(stroke=True),
                                             from_color=command.Color(10, 10, 10),
                                             to_color=command.Color(255, 255, 255)))

class ParseNonNegativeNumber(TestParse):
    tested_class_name = "NonNegativeNumber"

    def test_integer(self):
        self.assertEqual(self.parse("123").number, 123)

    def test_float(self):
        self.assertEqual(self.parse("1.2").number, 1.2)

    def test_zero(self):
        self.assertEqual(self.parse("0.0").number, 0.0)

class ParseLengthUnit(TestParse):
    tested_class_name = "LengthUnit"

    def test_pixels(self):
        self.assertEqual(self.parse("px").unit, "px")
        self.assertEqual(self.parse("pixel").unit, "px")
        self.assertEqual(self.parse("pixels").unit, "px")

    def test_points(self):
        self.assertEqual(self.parse("pt").unit, "pt")
        self.assertEqual(self.parse("point").unit, "pt")
        self.assertEqual(self.parse("points").unit, "pt")

    def test_millimeters(self):
        self.assertEqual(self.parse("mm").unit, "mm")
        self.assertEqual(self.parse("millimeter").unit, "mm")
        self.assertEqual(self.parse("millimeters").unit, "mm")

    def test_centimeters(self):
        self.assertEqual(self.parse("cm").unit, "cm")
        self.assertEqual(self.parse("centimeter").unit, "cm")
        self.assertEqual(self.parse("centimeters").unit, "cm")

class ParseLength(TestParse):
    tested_class_name = "Length"

    def test_default(self):
        self.assertEqual(self.parse("10").length, command.Length(10, "px"))

    def test_units(self):
        self.assertEqual(self.parse("5mm").length, command.Length(5, "mm"))
        self.assertEqual(self.parse("5", "centimeters").length, command.Length(5, "cm"))
        self.assertEqual(self.parse("0.5", "of", "pixel").length, command.Length(0.5, "px"))

class ParseDirection(TestParse):
    tested_class_name = "Direction"

    def test_horizontally(self):
        self.assertEqual(self.parse("horizontally").direction, "horizontally")
        self.assertEqual(self.parse("hor").direction, "horizontally")
        self.assertEqual(self.parse("x").direction, "horizontally")

    def test_vertically(self):
        self.assertEqual(self.parse("vertically").direction, "vertically")
        self.assertEqual(self.parse("ver").direction, "vertically")
        self.assertEqual(self.parse("y").direction, "vertically")

class ParseMove(TestParse):
    tested_class_name = "Move"

    def test_simple(self):
        self.assertEqual(self.parse("by", "10mm", "and", "by", "10", "cm").command,
                command.Move(
                    horizontally=command.Length(10, "mm"),
                    vertically=command.Length(10, "cm")))
        self.assertEqual(self.parse("5", "and", "by", "10", "centimeters").command,
                command.Move(
                    horizontally=command.Length(5, "px"),
                    vertically=command.Length(10, "cm")))
        self.assertEqual(self.parse("5", "3").command,
                command.Move(
                    horizontally=command.Length(5, "px"),
                    vertically=command.Length(3, "px")))

    def test_direction(self):
        self.assertEqual(self.parse(*("by 2mm horizontally and by 20 cm vertically".split())).command,
                command.Move(command.Length(2, "mm"), command.Length(20, "cm")))
        self.assertEqual(self.parse("2mm", "ver", "3", "hor").command,
                command.Move(command.Length(3), command.Length(2, "mm")))
        self.assertEqual(self.parse("1cm", "ver", "3").command,
                command.Move(command.Length(3), command.Length(1, "cm")))
        self.assertEqual(self.parse("1cm", "hor", "3").command,
                command.Move(command.Length(1, "cm"), command.Length(3)))
        self.assertEqual(self.parse("1cm", "3", "x").command,
                command.Move(command.Length(3), command.Length(1, "cm")))
        self.assertEqual(self.parse("1cm").command,
                command.Move(command.Length(1, "cm"), command.Length(0)))
        self.assertEqual(self.parse("1cm", "y").command,
                command.Move(command.Length(0), command.Length(1, "cm")))

class ParseSelect(TestParse):
    tested_class_name = "Select"

    def test_select(self):
        self.assertEqual(self.parse("select", "#foo_7").command, command.Select(id="foo_7"))
        self.assertEqual(self.parse("select", "#foo-bar").command, command.Select(id="foo-bar"))


