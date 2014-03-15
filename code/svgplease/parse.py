from modgrammar import *
from . import command

grammar_whitespace_mode = "explicit"

SEPARATOR = "\0"

def join_tokens(tokens):
    """Joins tokens to internal representation suitable for parsing."""
    return SEPARATOR.join(tokens) + SEPARATOR

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

class CommandList(Grammar):
    grammar = LIST_OF(OR(Open, Save), sep=("then", SEPARATOR))
    def grammar_elem_init(self, sessiondata):
        self.command_list = list(map(lambda r : r.command, list(self[0])[::2]))

class Number(Grammar):
    grammar = (OPTIONAL(OR("+", "-")), WORD("0-9"), OPTIONAL((".", WORD("0-9"))))
    def grammar_elem_init(self, sessiondata):
        self.number = float(self.string)

class Color(Grammar):
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

