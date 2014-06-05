import unittest

from svgplease import main

class TestExpand(unittest.TestCase):

    def test_quotes(self):
        self.assertEqual(
                main.expand("'abc'", '"cba"', "foo", "''foobar''"),
                ["abc", "cba", "foo", "foobar"])

    def test_backslash(self):
        self.assertEqual(main.expand("\\#foo", "10\\%"), ["#foo", "10%"])
