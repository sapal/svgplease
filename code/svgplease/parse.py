from modgrammar import *

grammar_whitespace_mode = "optional"

SEPARATOR = "\0"

def join_tokens(tokens):
    """Joins tokens to internal representation suitable for parsing."""
    return SEPARATOR.join(tokens) + SEPARATOR

class Filename(Grammar):
    grammar = OR(
            (EXCEPT(ANY_EXCEPT(SEPARATOR), OR("then", "file")), SEPARATOR),
            ("file", SEPARATOR, ANY_EXCEPT(SEPARATOR), SEPARATOR))
    grammar_whitespace_mode = "explicit"
    def grammar_elem_init(self, sessiondata):
        elements = self[0].elements
        self.filename = elements[0].string if len(elements) == 2 else elements[2].string

