import unittest

from svgplease.command import Open, Save

class TestOpen(unittest.TestCase):

    def test_filenames(self):
        self.assertEqual(Open("file.svg").filenames, ("file.svg",))

    def test_eq(self):
        self.assertEqual(Open("file.svg"), Open("file.svg"))
        self.assertNotEqual(Open("some file.svg"), Open("other file.svg"))
        self.assertNotEqual(Open("file.svg"), Save("file.svg"))

    def test_hash(self):
        self.assertEqual(
                hash(Open("file1.svg", "file2.svg")),
                hash(Open("file1.svg", "file2.svg")))
        self.assertNotEqual(
                hash(Open("file1.svg", "file2.svg")),
                hash(Open("file2.svg", "file1.svg")))

class TestSave(unittest.TestCase):

    def test_filenames(self):
        self.assertEqual(Save("file.svg").filenames, ("file.svg",))

    def test_eq(self):
        self.assertEqual(Save("file.svg"), Save("file.svg"))
        self.assertNotEqual(Save("some file.svg"), Save("other file.svg"))
        self.assertNotEqual(Save("file.svg"), Open("file.svg"))

    def test_hash(self):
        self.assertEqual(
                hash(Save("file1.svg", "file2.svg")),
                hash(Save("file1.svg", "file2.svg")))
        self.assertNotEqual(
                hash(Save("file1.svg", "file2.svg")),
                hash(Save("file2.svg", "file1.svg")))
