from modgrammar import *
from . import command

grammar_whitespace_mode = "explicit"

SEPARATOR = "\0"

def join_tokens(tokens):
    """Joins tokens to internal representation suitable for parsing."""
    if len(tokens) > 0:
        return SEPARATOR.join(tokens) + SEPARATOR
    else:
        return ""

class Filename(Grammar):
    grammar = OR(
            (EXCEPT(ANY_EXCEPT(SEPARATOR), OR("then", "file", "to")), SEPARATOR),
            ("file", SEPARATOR, ANY_EXCEPT(SEPARATOR), SEPARATOR))
    grammar_whitespace_mode = "explicit"
    def grammar_elem_init(self, sessiondata):
        elements = self[0].elements
        self.filename = elements[0].string if len(elements) == 2 else elements[2].string

class Open(Grammar):
    grammar = ("open", SEPARATOR, ONE_OR_MORE(Filename))
    def grammar_elem_init(self, sessiondata):
        filenames = map(lambda g : g.filename, self[2])
        self.command = command.Open(*filenames)

class Save(Grammar):
    grammar = ("save", SEPARATOR, OPTIONAL(("to", SEPARATOR)), ONE_OR_MORE(Filename))
    def grammar_elem_init(self, sessiondata):
        filenames = map(lambda g : g.filename, self[3])
        self.command = command.Save(*filenames)

class Number(Grammar):
    grammar = (OPTIONAL(OR("+", "-")), WORD("0-9"), OPTIONAL((".", WORD("0-9"))), SEPARATOR)
    def grammar_elem_init(self, sessiondata):
        self.number = float(self.string[:-len(SEPARATOR)])

class Color(Grammar):
    #TODO: color names
    grammar = OR(
            ("#", WORD("0-9a-fA-F", min=6, max=6),
            OPTIONAL(WORD("0-9a-fA-F", min=2, max=2)), SEPARATOR),
            ("rgb(", LIST_OF((OPTIONAL(WHITESPACE),
                OR(("25", WORD("0-5", min=1, max=1)),
                   ("2", WORD("0-4", "0-9", min=2, max=2)),
                   (OPTIONAL(WORD("0-1", min=1, max=1)), WORD("0-9", min=0, max=2))),
                OPTIONAL(WHITESPACE)), sep=",", min=3, max=3), ")", SEPARATOR))

    def grammar_elem_init(self, sessiondata):
        alpha = None
        if self.string[0] == "#":
            value = self.string[1:7]
            rgb = map(lambda x : int(x, 16), (value[0:2], value[2:4], value[4:6]))
            if self[0][2] is not None:
                alpha = int(self.string[7:9], 16)
        else:
            value = self.string[4:-1-len(SEPARATOR)]
            rgb = map(lambda d : int(d.strip()), value.split(","))
        self.color = command.Color(*rgb, alpha=alpha)

class FillStroke(Grammar):
    grammar = OR(EMPTY,
            (OR(("fill", OPTIONAL((OPTIONAL((SEPARATOR, "and")), (SEPARATOR, "stroke")))),
                ("stroke", OPTIONAL((OPTIONAL((SEPARATOR, "and")), (SEPARATOR, "fill"))))),
             SEPARATOR))
    def grammar_elem_init(self, sessiondata):
        fill = True if "fill" in self.string else None
        stroke = True if "stroke" in self.string else None
        self.fill_stroke = command.FillStroke(fill=fill, stroke=stroke)

class ChangeColor(Grammar):
    grammar = ("change", SEPARATOR, FillStroke, OPTIONAL(("color", SEPARATOR)),
               OPTIONAL(OPTIONAL(("from", SEPARATOR)), Color),
               OPTIONAL(("to", SEPARATOR)), Color)
    def grammar_elem_init(self, sessiondata):
        from_color = None if self[4] is None else self[4][1].color
        self.command = command.ChangeColor(fill_stroke=self[2].fill_stroke,
                                           from_color=from_color,
                                           to_color=self[6].color)

class CommandList(Grammar):
    grammar = LIST_OF(OR(ChangeColor, Open, Save), sep=("then", SEPARATOR))
    def grammar_elem_init(self, sessiondata):
        self.command_list = list(map(lambda r : r.command, list(self[0])[::2]))

class NonNegativeNumber(Grammar):
    grammar = (OPTIONAL("+"), WORD("0-9"), OPTIONAL((".", WORD("0-9"))), SEPARATOR)
    def grammar_elem_init(self, sessiondata):
        self.number = float(self.string[:-len(SEPARATOR)])

class LengthUnit(Grammar):
    grammar = (OR(
        OR("px", "pixel", "pixels"),
        OR("pt", "point", "points"),
        OR("mm", "millimeter", "millimeters"),
        OR("cm", "centimeter", "centimeters")
        ), SEPARATOR)
    unit_map = {
            "px": "px",
            "pixel": "px",
            "pixels": "px",
            "pt": "pt",
            "point": "pt",
            "points": "pt",
            "mm": "mm",
            "millimeter": "mm",
            "millimeters": "mm",
            "cm": "cm",
            "centimeter": "cm",
            "centimeters": "cm",
        }
    def grammar_elem_init(self, sessiondata):
        self.unit = LengthUnit.unit_map[self[0].string]

