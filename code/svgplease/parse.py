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

def KeywordBase(keyword, type, optional=False):
    """Base for all *Keyword functions below"""
    grammar = GRAMMAR(LITERAL(keyword), LITERAL(SEPARATOR))
    if optional:
        grammar = OPTIONAL(grammar)
    grammar.grammar_error_override = True
    grammar.completions = [keyword]
    grammar.type = type
    def prefix_matches(prefix):
        return keyword[:len(prefix)] == prefix
    grammar.prefix_matches = prefix_matches
    return grammar

def CommandKeyword(keyword):
    """Literal command keyword"""
    return KeywordBase(keyword, "command")

def Keyword(keyword):
    """Literal non-command keyword"""
    return KeywordBase(keyword, "keyword")

def OptionalKeyword(keyword):
    """Literal optional keyword"""
    return KeywordBase(keyword, "optional_keyword", optional=True)

class Filename(Grammar):
    grammar = OR(
            (EXCEPT(ANY_EXCEPT(SEPARATOR), OR("then", "file", "to")), SEPARATOR),
            ("file", SEPARATOR, ANY_EXCEPT(SEPARATOR), SEPARATOR))
    grammar_whitespace_mode = "explicit"
    def grammar_elem_init(self, sessiondata):
        elements = self[0].elements
        self.filename = elements[0].string if len(elements) == 2 else elements[2].string

class Open(Grammar):
    grammar = (CommandKeyword("open"), ONE_OR_MORE(Filename))
    def grammar_elem_init(self, sessiondata):
        filenames = map(lambda g : g.filename, self[1])
        self.command = command.Open(*filenames)

class Save(Grammar):
    grammar = (CommandKeyword("save"), OPTIONAL(("to", SEPARATOR)), ONE_OR_MORE(Filename))
    def grammar_elem_init(self, sessiondata):
        filenames = map(lambda g : g.filename, self[2])
        self.command = command.Save(*filenames)

class NumberWithoutSeparator(Grammar):
    grammar = (OPTIONAL(OR("+", "-")), WORD("0-9"), OPTIONAL((".", WORD("0-9"))))
    def grammar_elem_init(self, sessiondata):
        self.number = float(self.string)

class Number(Grammar):
    grammar = (NumberWithoutSeparator, SEPARATOR)
    def grammar_elem_init(self, sessiondata):
        self.number = self[0].number

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
    grammar = (CommandKeyword("change"), FillStroke, OPTIONAL(("color", SEPARATOR)),
               OPTIONAL(OPTIONAL(("from", SEPARATOR)), Color),
               OPTIONAL(("to", SEPARATOR)), Color)
    def grammar_elem_init(self, sessiondata):
        from_color = None if self[3] is None else self[3][1].color
        self.command = command.ChangeColor(fill_stroke=self[1].fill_stroke,
                                           from_color=from_color,
                                           to_color=self[5].color)

class NonNegativeNumberWithoutSeparator(Grammar):
    grammar = (OPTIONAL("+"), WORD("0-9"), OPTIONAL((".", WORD("0-9"))))
    def grammar_elem_init(self, sessiondata):
        self.number = float(self.string)

class NonNegativeNumber(Grammar):
    grammar = (NonNegativeNumberWithoutSeparator, SEPARATOR)
    def grammar_elem_init(self, sessiondata):
        self.number = self[0].number

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

class Length(Grammar):
    grammar = (NonNegativeNumberWithoutSeparator, OPTIONAL(SEPARATOR),
            OPTIONAL(OPTIONAL("of", SEPARATOR), LengthUnit))
    def grammar_elem_init(self, sessiondata):
        self.length = command.Length(self[0].number, "px" if self[2] is None else self[2][1].unit)

class Displacement(Grammar):
    grammar = (NumberWithoutSeparator, OPTIONAL(SEPARATOR),
            OPTIONAL(OPTIONAL("of", SEPARATOR), LengthUnit))
    def grammar_elem_init(self, sessiondata):
        self.displacement = command.Length(self[0].number, "px" if self[2] is None else self[2][1].unit)

class Direction(Grammar):
    grammar = (OR("horizontally", "hor", "x", "vertically", "ver", "y"), SEPARATOR)
    def grammar_elem_init(self, sessiondata):
        self.direction = "horizontally" if self.string[:-len(SEPARATOR)] in ("horizontally", "hor", "x") else "vertically"

def other_direction(direction):
    """Returns the other direction."""
    if direction == "horizontally":
        return "vertically"
    else:
        return "horizontally"

class Move(Grammar):
    grammar = (CommandKeyword("move"), OPTIONAL("by", SEPARATOR), Displacement, OPTIONAL(Direction),
            OPTIONAL(OPTIONAL("and", SEPARATOR, "by", SEPARATOR), Displacement, OPTIONAL(Direction)))
    def grammar_elem_init(self, sessiondata):
        displacement1 = self[2].displacement
        displacement2 = self[4][1].displacement if self[4] else command.Displacement(0)
        direction1 = self[3].direction if self[3] else None
        direction2 = self[4][2].direction if self[4] and self[4][2] else None

        if direction1 == None and direction2 == None:
            direction1 = "horizontally"
            direction2 = "vertically"
        elif direction1 == None:
            direction1 = other_direction(direction2)
        elif direction2 == None:
            direction2 = other_direction(direction1)

        self.command = command.Move(**{
            direction1: displacement1,
            direction2: displacement2,
            })

class Select(Grammar):
    grammar = (CommandKeyword("select"), "#", WORD("-_a-zA-Z0-9"), SEPARATOR)
    def grammar_elem_init(self, sessiondata):
        self.command = command.Select(self[2].string)

class Percent(Grammar):
    grammar = (NumberWithoutSeparator, "%", SEPARATOR)
    def grammar_elem_init(self, sessiondata):
        self.percent = self[0].number
        self.number = self.percent / 100

class Scale(Grammar):
    grammar = (CommandKeyword("scale"), OPTIONAL("by", SEPARATOR), OR(Number, Percent), OR(
        OPTIONAL("both", SEPARATOR, OPTIONAL("directions", SEPARATOR)),
        (OPTIONAL(Direction), OPTIONAL(OPTIONAL("and", SEPARATOR, OPTIONAL("by", SEPARATOR)), OR(Number, Percent), OPTIONAL(Direction)))))
    def grammar_elem_init(self, sessiondata):
        both = (self[3] is None or self[3].string[:4] in ("", "both"))
        scale1 = self[2].number
        if both:
            self.command = command.Scale(scale1, scale1)
        else:
            scale2 = 1
            if self[3][1] and self[3][1][1]:
                scale2 = self[3][1][1].number
            direction1 = self[3][0].direction if self[3][0] else None
            direction2 = self[3][1][2].direction if self[3][1] and self[3][1][2] else None
            if direction1 is None and direction2 is None:
                direction1, direction2 = "horizontally", "vertically"
            elif direction1 == None:
                direction1 = other_direction(direction2)
            elif direction2 == None:
                direction2 = other_direction(direction1)
            self.command = command.Scale(**{
                direction1: scale1,
                direction2: scale2
                })

class Remove(Grammar):
    grammar = (CommandKeyword("remove"), OptionalKeyword("selected"))
    def grammar_elem_init(self, sessiondata):
        self.command = command.Remove()

class CommandList(Grammar):
    grammar = LIST_OF(OR(ChangeColor, Move, Open, Remove, Save, Scale, Select), sep=Keyword("then"))
    def grammar_elem_init(self, sessiondata):
        self.command_list = list(map(lambda r : r.command, list(self[0])[::2]))

def complete(*tokens):
    text = join_tokens(tokens) + SEPARATOR
    try:
        CommandList.parser().parse_text(text, eof=True, matchtype="complete")
    except ParseError as e:
        suffix = text[e.char:].rstrip(SEPARATOR)
        completions = {}
        for grammar in e.expected:
            if not "prefix_matches" in dir(grammar) or not grammar.prefix_matches(suffix):
                continue
            if grammar.type not in completions:
                completions[grammar.type] = []
            completions[grammar.type].extend(grammar.completions)
        sorted_completions = {}
        for key, value in completions.items():
            sorted_completions[key] = sorted(value)
        return sorted_completions
