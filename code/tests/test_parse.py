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

    def test_remove_command(self):
        self.assertEqual(self.parse("remove", "selected").command_list, [command.Remove()])

    def test_save_command(self):
        self.assertEqual(self.parse("save", "to", "file2.svg").command_list, [command.Save("file2.svg")])

    def test_scale_command(self):
        self.assertEqual(self.parse("scale", "by", "2").command_list, [command.Scale(2, 2)])

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

class ParseDisplacement(TestParse):
    tested_class_name = "Displacement"

    def test_default(self):
        self.assertEqual(self.parse("10").displacement, command.Displacement(10, "px"))

    def test_units(self):
        self.assertEqual(self.parse("-5mm").displacement, command.Displacement(-5, "mm"))
        self.assertEqual(self.parse("5", "centimeters").displacement, command.Displacement(5, "cm"))
        self.assertEqual(self.parse("-0.5", "of", "pixel").displacement, command.Displacement(-0.5, "px"))

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
        self.assertEqual(self.parse("move", "by", "10mm", "and", "by", "10", "cm").command,
                command.Move(
                    horizontally=command.Displacement(10, "mm"),
                    vertically=command.Displacement(10, "cm")))
        self.assertEqual(self.parse("move", "by", "-10mm", "and", "by", "-10", "cm").command,
                command.Move(
                    horizontally=command.Displacement(-10, "mm"),
                    vertically=command.Displacement(-10, "cm")))
        self.assertEqual(self.parse("move", "5", "and", "by", "10", "centimeters").command,
                command.Move(
                    horizontally=command.Displacement(5, "px"),
                    vertically=command.Displacement(10, "cm")))
        self.assertEqual(self.parse("move", "5", "3").command,
                command.Move(
                    horizontally=command.Displacement(5, "px"),
                    vertically=command.Displacement(3, "px")))

    def test_direction(self):
        self.assertEqual(self.parse(*("move by 2mm horizontally and by 20 cm vertically".split())).command,
                command.Move(command.Displacement(2, "mm"), command.Displacement(20, "cm")))
        self.assertEqual(self.parse("move", "2mm", "ver", "3", "hor").command,
                command.Move(command.Displacement(3), command.Displacement(2, "mm")))
        self.assertEqual(self.parse("move", "1cm", "ver", "3").command,
                command.Move(command.Displacement(3), command.Displacement(1, "cm")))
        self.assertEqual(self.parse("move", "1cm", "hor", "3").command,
                command.Move(command.Displacement(1, "cm"), command.Displacement(3)))
        self.assertEqual(self.parse("move", "1cm", "3", "x").command,
                command.Move(command.Displacement(3), command.Displacement(1, "cm")))
        self.assertEqual(self.parse("move", "1cm").command,
                command.Move(command.Displacement(1, "cm"), command.Displacement(0)))
        self.assertEqual(self.parse("move", "1cm", "y").command,
                command.Move(command.Displacement(0), command.Displacement(1, "cm")))

class ParseSelect(TestParse):
    tested_class_name = "Select"

    def test_select(self):
        self.assertEqual(self.parse("select", "#foo_7").command, command.Select(id="foo_7"))
        self.assertEqual(self.parse("select", "#foo-bar").command, command.Select(id="foo-bar"))

class ParsePercent(TestParse):
    tested_class_name = "Percent"

    def test_percent(self):
        self.assertEqual(self.parse("50%").percent, 50)
        self.assertEqual(self.parse("200.03%").percent, 200.03)
        self.assertEqual(self.parse("-50%").percent, -50)

    def test_number(self):
        self.assertEqual(self.parse("50%").number, 0.50)

class ParseScale(TestParse):
    tested_class_name = "Scale"

    def test_scale(self):
        self.assertEqual(self.parse(*("scale by 50% both directions".split())).command, command.Scale(0.5, 0.5))
        self.assertEqual(self.parse(*("scale by 50% and by 75%".split())).command, command.Scale(0.5, 0.75))
        self.assertEqual(self.parse(*("scale 2 y 4 x".split())).command, command.Scale(4, 2))
        self.assertEqual(self.parse(*("scale 2 40%".split())).command, command.Scale(2, 0.4))
        self.assertEqual(self.parse(*("scale 2 x".split())).command, command.Scale(horizontally=2))
        self.assertEqual(self.parse(*("scale 2 y".split())).command, command.Scale(vertically=2))
        self.assertEqual(self.parse(*("scale by 2".split())).command, command.Scale(2, 2))

class ParseRemove(TestParse):
    tested_class_name = "Remove"

    def test_remove(self):
        self.assertEqual(self.parse("remove").command, command.Remove())
        self.assertEqual(self.parse("remove", "selected").command, command.Remove())

class Complete(unittest.TestCase):

    def assertCompletionEqual(self, tokens, expected_completion):
        self.assertEqual(svgplease.parse.complete(*tokens), expected_completion)

    def assertCompletionContains(self, tokens, expected_completion):
        completion = svgplease.parse.complete(*tokens)
        print(completion, expected_completion)
        self.assertTrue(all(item in completion.items() for item in expected_completion.items()))

    def test_complete_command(self):
        self.assertCompletionEqual([], {
            "command": ["change", "move", "open", "remove", "save", "scale", "select"]
            })

        self.assertCompletionEqual(["s"], {
            "command": ["save", "scale", "select"]
            })

    def test_complete_commands(self):
        self.assertCompletionContains(["remove"], {
            "keyword": ["then"]
            })

    def test_complete_remove(self):
        self.assertCompletionContains(["remove"], {
            "optional_keyword": ["selected"]
            })

    def test_complete_change(self):
        self.assertCompletionEqual(["change"], {
            "fill_or_stroke": ["fill", "stroke"],
            "optional_keyword": ["color", "from", "to"],
            "color": ["#rrggbb", "#rrggbbaa"],
            })

        self.assertCompletionEqual(["change", "fill"], {
            "fill_or_stroke": ["stroke"],
            "optional_keyword": ["and", "color", "from", "to"],
            "color": ["#rrggbb", "#rrggbbaa"],
            })

        self.assertCompletionEqual(["change", "stroke"], {
            "fill_or_stroke": ["fill"],
            "optional_keyword": ["and", "color", "from", "to"],
            "color": ["#rrggbb", "#rrggbbaa"],
            })

    def test_complete_move(self):
        self.assertCompletionEqual(["move"], {
            "optional_keyword": ["by"],
            "number": ["-0.5", "10"],
            })

        self.assertCompletionEqual(["move", "10"], {
            "direction": ["hor", "horizontally", "ver", "vertically", "x", "y"],
            "unit": ["centimeter", "centimeters", "cm", "millimeter", "millimeters", "mm", "pixel", "pixels", "point", "points", "pt", "px"],
            "optional_keyword": ["and", "of"],
            "number": ["-0.5", "10"],
            "keyword": ["then"],
            })

    def test_complete_open(self):
        self.assertCompletionEqual(["open"], {
            "keyword": ["file"],
            "file": ["file.svg"],
            })

        self.assertCompletionEqual(["open", "file"], {
            "file": ["file.svg"],
            })

        self.assertCompletionEqual(["open", "file.svg"], {
            "keyword": ["file", "then"],
            "file": ["file.svg"],
            })

    def test_complete_save(self):
        self.assertCompletionEqual(["save"], {
            "optional_keyword": ["to"],
            "keyword": ["file"],
            "file": ["file.svg"],
            })

    def test_complete_scale(self):
        self.assertCompletionEqual(["scale"], {
            "optional_keyword": ["by"],
            "number": ["-0.5", "10"],
            "percent": ["-25%", "150%"],
            })

        self.assertCompletionEqual(["scale", "by", "2"], {
            "optional_keyword": ["and", "both"],
            "direction": ["hor", "horizontally", "ver", "vertically", "x", "y"],
            "number": ["-0.5", "10"],
            "percent": ["-25%", "150%"],
            "keyword": ["then"],
            })

