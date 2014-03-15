import os
import unittest
from xml.etree import ElementTree
from . import util

from svgplease.command import Color, ExecutionContext, FillStroke, Open, Save, SVGRoot

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

    def test_execute(self):
        execution_context = ExecutionContext()
        execution_context.svg_roots.append(object())
        with util.TestDirectory(os.path.join(util.TEST_DATA, "circle.svg")) as testdir:
            filename = os.path.join(testdir, "circle.svg")
            Open(filename).execute(execution_context)
            self.assertEqual(len(execution_context.svg_roots), 2)
            root = execution_context.svg_roots[1]
            self.assertIsInstance(root.root_element, ElementTree.ElementTree)
            self.assertEqual(root.filename, filename)

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

    def test_execute(self):
        execution_context = ExecutionContext()
        with util.TestDirectory(os.path.join(util.TEST_DATA, "circle.svg")) as testdir:
            filename = os.path.join(testdir, "circle.svg")
            svg_root = ElementTree.parse(filename)
            for i in range(4):
                execution_context.svg_roots.append(SVGRoot(svg_root, "circle.svg"))
            names = list(map(
                lambda f : os.path.join(testdir, f),
                ("output0.svg", "output1.svg", "output1.svg")))
            Save(*names).execute(execution_context)
            for name in ("output0.svg", "output1.svg", "output2.svg", "output3.svg"):
                self.assertTrue(os.path.isfile(os.path.join(testdir, name)))

class TestExecutionContext(unittest.TestCase):

    def test_svg_roots(self):
        self.assertEqual(ExecutionContext().svg_roots, [])

class TestSVGRoot(unittest.TestCase):

    def test_filename(self):
        root_element = object()
        self.assertEqual(SVGRoot(root_element).filename, "image.svg")
        self.assertEqual(SVGRoot(root_element, "file.svg").filename, "file.svg")

    def test_root_element(self):
        root_element = object()
        self.assertEqual(SVGRoot(root_element).root_element, root_element)

class TestColor(unittest.TestCase):

    def test_rgb(self):
        color = Color(13, 16, 255)
        self.assertEqual(color.rgb, (13, 16, 255))

    def test_alpha(self):
        color = Color(0, 255, 10, 127)
        self.assertEqual(color.rgba, (0, 255, 10, 127))
        self.assertEqual(color.alpha, 127)
        color = Color(10, 20, 30)
        self.assertEqual(color.alpha, None)

    def test_str(self):
        color = Color(0, 255, 10)
        self.assertEqual(str(color), "#00ff0a")

    def test_eq(self):
        self.assertEqual(Color(0, 255, 10), Color(0, 255, 10))
        self.assertEqual(Color(0, 0, 0, 50), Color(0, 0, 0, 50))
        self.assertNotEqual(Color(0, 0, 0, 0), Color(0, 0, 0))

class TestFillStroke(unittest.TestCase):

    def test_default(self):
        fill_stroke = FillStroke()
        self.assertEqual(fill_stroke.fill, True)
        self.assertEqual(fill_stroke.stroke, True)

    def test_constructor(self):
        fill_stroke = FillStroke(fill=True)
        self.assertEqual(fill_stroke.fill, True)
        self.assertEqual(fill_stroke.stroke, False)
        fill_stroke = FillStroke(stroke=True)
        self.assertEqual(fill_stroke.fill, False)
        self.assertEqual(fill_stroke.stroke, True)

    def test_eq(self):
        self.assertEqual(FillStroke(), FillStroke())
        self.assertEqual(FillStroke(fill=True), FillStroke(fill=True))
        self.assertNotEqual(FillStroke(), FillStroke(stroke=True))
