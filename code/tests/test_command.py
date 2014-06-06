import os
import unittest
from xml.etree import ElementTree
from . import util

from svgplease.command import ChangeColor, ChangeFontFamily, ChangeLike, ChangeText, Color, Displacement, ExecutionContext, FillStroke, Length, Open, Move, Page, Remove, Save, Scale, Select, SVGRoot, Tile

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
            self.assertEqual(len(execution_context.selected_nodes), 1)
            self.assertIsInstance(execution_context.selected_nodes[0], ElementTree.Element)
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

    def test_selected_nodes(self):
        self.assertEqual(ExecutionContext().selected_nodes, [])

    def test_copy(self):
        context = ExecutionContext()
        context.svg_roots = ["foo", "bar"]
        context.selected_nodes = ["lol"]
        copy = context.copy()
        copy.svg_roots = ["foobar"]
        copy.selected_nodes = ["LOL"]
        self.assertEqual(context.svg_roots, ["foo", "bar"])
        self.assertEqual(context.selected_nodes, ["lol"])

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
        self.assertNotEqual(Color(0, 0, 0, 0), None)

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

class TestChangeColor(unittest.TestCase):

    def test_attributes(self):
        fill_stroke = object()
        from_color = object()
        to_color = object()
        change_color = ChangeColor(fill_stroke=fill_stroke, from_color=from_color, to_color=to_color)
        self.assertEqual(change_color.fill_stroke, fill_stroke)
        self.assertEqual(change_color.from_color, from_color)
        self.assertEqual(change_color.to_color, to_color)
        self.assertEqual(ChangeColor(fill_stroke=fill_stroke, to_color=to_color).from_color, None)

    def test_eq(self):
        fill_stroke = object()
        from_color = object()
        to_color = object()
        self.assertEqual(ChangeColor(fill_stroke=fill_stroke, to_color=to_color, from_color=from_color),
                         ChangeColor(fill_stroke=fill_stroke, to_color=to_color, from_color=from_color))
        self.assertNotEqual(ChangeColor(fill_stroke=fill_stroke, to_color=to_color, from_color=from_color),
                            ChangeColor(fill_stroke=fill_stroke, to_color=object(), from_color=from_color))

    def test_execute(self):
        # More usecases are covered by set-color usecase test.
        execution_context = ExecutionContext()
        with util.TestDirectory(os.path.join(util.TEST_DATA, "circle.svg")) as testdir:
            t = ElementTree.parse(os.path.join(testdir, "circle.svg"))
            execution_context.selected_nodes.append(t.getroot())
            command = ChangeColor(
                    fill_stroke=FillStroke(),
                    from_color=Color(0, 0, 0),
                    to_color=Color(255, 0, 0))
            command.execute(execution_context)
            self.assertEqual(t.getroot()[0].attrib["stroke"], "#ff0000")

class TestLength(unittest.TestCase):

    def test_eq(self):
        self.assertEqual(Length(10, "px"), Length(10, "px"))
        self.assertEqual(Length(10, "px"), Length(10))
        self.assertNotEqual(Length(10, "cm"), Length(10, "px"))
        self.assertNotEqual(Length(11, "px"), Length(10, "px"))

    def test_in_pixels(self):
        global DPI
        DPI = 120
        self.assertEqual(Length(10).in_pixels(), 10)
        self.assertEqual(Length(10, "mm").in_pixels(), 47.24409444)
        self.assertEqual(Length(10, "cm").in_pixels(), 472.4409444)
        self.assertEqual(Length(10, "pt").in_pixels(), 12.5)

    def test_str(self):
        self.assertEqual(str(Length(11, "px")), "11 px")

    def test_repr(self):
        self.assertEqual(repr(Length(15, "mm")), "Length(15, 'mm')")

class TestDisplacement(unittest.TestCase):

    def test_eq(self):
        self.assertEqual(Displacement(10, "px"), Displacement(10, "px"))
        self.assertEqual(Displacement(-10, "px"), Displacement(-10))
        self.assertNotEqual(Displacement(10, "cm"), Displacement(10, "px"))
        self.assertNotEqual(Displacement(-10, "cm"), Displacement(10, "cm"))
        self.assertNotEqual(Displacement(-11, "px"), Displacement(-10, "px"))

    def test_in_pixels(self):
        global DPI
        DPI = 120
        self.assertEqual(Displacement(10).in_pixels(), 10)
        self.assertEqual(Displacement(-10, "mm").in_pixels(), -47.24409444)
        self.assertEqual(Displacement(10, "cm").in_pixels(), 472.4409444)
        self.assertEqual(Displacement(-10, "pt").in_pixels(), -12.5)

class TestMove(unittest.TestCase):

    def test_eq(self):
        self.assertEqual(Move(horizontally=Length(10), vertically=Length(5)), Move(Length(10), Length(5)))
        self.assertNotEqual(Move(Length(3), Length(4)), Move(Length(2), Length(4)))
        self.assertNotEqual(Move(Length(3), Length(4)), Move(Length(3), Length(2)))

    def test_execute(self):
        # More usecases are covered by move-relative usecase test.
        execution_context = ExecutionContext()
        with util.TestDirectory(os.path.join(util.TEST_DATA, "rectangles.svg")) as testdir:
            root = ElementTree.parse(os.path.join(testdir, "rectangles.svg")).getroot()
            rect = root.findall(".//*[@id='blue']")[0]
            execution_context.selected_nodes = [rect]

            self.assertEqual(rect.get("transform"), None)
            Move(Length(10), Length(20)).execute(execution_context)
            self.assertEqual(rect.get("transform"), "translate(10,20)")
            Move(Length(30), Length(40)).execute(execution_context)
            self.assertEqual(rect.get("transform"), "translate(30,40) translate(10,20)")
            rect.set("transform", None)
            Move(Length(20, "mm"), Length(3, "cm")).execute(execution_context)
            self.assertEqual(rect.get("transform"), "translate(94.48818888,141.73228332)")


class TestSelect(unittest.TestCase):

    def test_eq(self):
        self.assertEqual(Select(id="foo"), Select("foo"))
        self.assertNotEqual(Select("foo"), Select("bar"))

    def test_execute(self):
        execution_context = ExecutionContext()
        with util.TestDirectory(os.path.join(util.TEST_DATA, "rectangles.svg")) as testdir:
            root = ElementTree.parse(os.path.join(testdir, "rectangles.svg")).getroot()

            execution_context.selected_nodes = [root]
            Select("blue").execute(execution_context)
            self.assertEqual(len(execution_context.selected_nodes), 1)
            self.assertEqual(execution_context.selected_nodes[0].get("id"), "blue")

            execution_context.selected_nodes = [root]
            Select("purple").execute(execution_context)
            self.assertEqual(len(execution_context.selected_nodes), 0)

class TestScale(unittest.TestCase):

    def test_eq(self):
        self.assertEqual(Scale(horizontally=2, vertically=3), Scale(2, 3))
        self.assertEqual(Scale(vertically=3), Scale(1, 3))
        self.assertEqual(Scale(horizontally=2), Scale(2, 1))
        self.assertNotEqual(Scale(3, 3), Scale(2, 3))
        self.assertNotEqual(Scale(3, 4), Scale(3, 3))

    def test_execute(self):
        # More usecases are covered by scale usecase test.
        execution_context = ExecutionContext()
        with util.TestDirectory(os.path.join(util.TEST_DATA, "rectangles.svg")) as testdir:
            root = ElementTree.parse(os.path.join(testdir, "rectangles.svg")).getroot()
            rect = root.findall(".//*[@id='blue']")[0]
            execution_context.selected_nodes = [rect]

            self.assertEqual(rect.get("transform"), None)
            Scale(2, 3).execute(execution_context)
            self.assertEqual(rect.get("transform"), "scale(2,3)")
            Scale(5, 0.5).execute(execution_context)
            self.assertEqual(rect.get("transform"), "scale(5,0.5) scale(2,3)")

class TestRemove(unittest.TestCase):

    def test_eq(self):
        self.assertEqual(Remove(), Remove())

    def test_execute(self):
        # More usecases are covered by scale usecase test.
        execution_context = ExecutionContext()
        with util.TestDirectory(os.path.join(util.TEST_DATA, "rectangles.svg")) as testdir:
            root = ElementTree.parse(os.path.join(testdir, "rectangles.svg")).getroot()
            execution_context.svg_roots = [SVGRoot(root, "rectangle.svg")]
            rect = root.findall(".//*[@id='blue']")[0]
            execution_context.selected_nodes = [rect]

            Remove().execute(execution_context)
            self.assertEqual(len(execution_context.selected_nodes), 0)
            self.assertEqual(len(root.findall(".//*[@id='blue']")), 0)

class TestChangeLike(unittest.TestCase):

    def test_eq(self):
        self.assertEqual(ChangeLike("from.svg", "to.svg"), ChangeLike("from.svg", "to.svg"))
        self.assertNotEqual(ChangeLike("a.svg", "b.svg"), ChangeLike("A.svg", "b.svg"))
        self.assertNotEqual(ChangeLike("a.svg", "b.svg"), ChangeLike("a.svg", "B.svg"))

    def test_execute(self):
        # Usecases are covered by change_like usecase test.
        pass

class TestChangeText(unittest.TestCase):

    def test_eq(self):
        self.assertEqual(ChangeText("abc"), ChangeText("abc"))
        self.assertNotEqual(ChangeText("ABC"), ChangeText("abc"))

    def test_execute(self):
        # Usecases are covered by change_like usecase test.
        pass

    def test_str(self):
        self.assertEqual(str(ChangeText("abc")), "ChangeText('abc')")

    def test_repr(self):
        self.assertEqual(repr(ChangeText("abc")), "ChangeText('abc')")

class TestPage(unittest.TestCase):

    def test_dimensions(self):
        w = Length(15, "mm")
        h = Length(3, "cm")
        self.assertEqual(Page(w, h).width, w)
        self.assertEqual(Page(w, h).height, h)

    def test_eq(self):
        w = Length(10, "cm")
        h = Length(500, "px")
        self.assertEqual(Page(w, h), Page(w, h))
        self.assertNotEqual(Page(w, h), Page(h, w))

    def test_a(self):
        self.assertEqual(Page("a3"), Page(Length(297, "mm"), Length(420, "mm")))
        self.assertEqual(Page("a4"), Page(Length(210, "mm"), Length(297, "mm")))
        self.assertEqual(Page("a5"), Page(Length(148, "mm"), Length(210, "mm")))

    def test_str(self):
        self.assertEqual(str(Page(Length(30, "mm"), Length(40, "mm"))), "Page(30 mm, 40 mm)")

    def test_repr(self):
        self.assertEqual(repr(Page(Length(30, "mm"), Length(40, "mm"))), "Page(Length(30, 'mm'), Length(40, 'mm'))")

class TestTile(unittest.TestCase):

    def test_fields(self):
        p = object()
        self.assertEqual(Tile(p, True).page, p)
        self.assertEqual(Tile(p, True).fill, True)
        self.assertEqual(Tile(p, False).fill, False)

    def test_eq(self):
        p, q = object(), object()
        self.assertEqual(Tile(p, True), Tile(p, True))
        self.assertNotEqual(Tile(p, True), Tile(q, True))
        self.assertNotEqual(Tile(p, True), Tile(p, False))

class TestChangeFontFamily(unittest.TestCase):

    def test_fields(self):
        self.assertEqual(ChangeFontFamily("Helvetica").font, "Helvetica")

    def test_eq(self):
        self.assertEqual(ChangeFontFamily("Times New Roman"), ChangeFontFamily("Times New Roman"))
        self.assertNotEqual(ChangeFontFamily("Verdana"), ChangeFontFamily("Helvetica"))
