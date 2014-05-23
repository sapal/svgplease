from xml.etree import ElementTree
import itertools
import math
import os
import re

"""Global DPI (dots per inch) setting."""
DPI = 120

ElementTree.register_namespace("", "http://www.w3.org/2000/svg")

class CommandBase(object):
    """Base class for all commands."""

    def execute(self, execution_context):
        """Execute this command using given execution context.

        This method should be overriden by individual commands.
        """
        pass

class OpenSaveBase(CommandBase):
    """Base class for Open and Save commands."""
    def __init__(self, *filenames):
        self.filenames = filenames

    def __eq__(self, other):
        if not issubclass(other.__class__, self.__class__): return False
        return self.filenames == other.filenames

    def __hash__(self):
        return hash(self.filenames)

class Open(OpenSaveBase):
    """Command for opening files"""
    def execute(self, execution_context):
        for filename in self.filenames:
            t = ElementTree.parse(filename)
            execution_context.svg_roots.append(SVGRoot(t, filename))
            execution_context.selected_nodes.append(t.getroot())

class Save(OpenSaveBase):
    """Command for saving files"""
    def execute(self, execution_context):
        used_filenames = set()
        def filename_generator(filename):
            yield filename
            if filename[-4:] != ".svg":
                filename += ".svg"
                yield filename
            if not re.search("[0-9]+", os.path.basename(filename)):
                base = filename[:-4]
                ending = filename[-4:]
                index = 0
            else:
                match = list(re.finditer("[0-9]+", filename))[-1]
                base = filename[:match.start()]
                ending = filename[match.end():]
                index = int(match.group())
            while True:
                index += 1
                yield base + str(index) + ending
        def generate_unique_filename(filename):
            for name in filename_generator(filename):
                if name not in used_filenames:
                    return name
        for svg_root, filename in zip(
                execution_context.svg_roots,
                itertools.chain(self.filenames, itertools.cycle(self.filenames[-1:]))):
            filename = generate_unique_filename(filename)
            used_filenames.add(filename)
            svg_root.root_element.write(filename, encoding="utf-8", xml_declaration=True)

class ExecutionContext(object):
    """Class for storing execution context for the commands.

    It has the following fields:
        - svg_roots - stores root elements for all opened/generated svg files
        - selected_nodes - stores subset of nodes of all opened/generated svg files
    """

    def __init__(self):
        self.svg_roots = []
        self.selected_nodes = []

    def copy(self):
        context = ExecutionContext()
        context.svg_roots = list(self.svg_roots)
        context.selected_nodes = list(self.selected_nodes)
        return context

class SVGRoot(object):
    """Class representing the root node of SVG file."""
    def __init__(self, root_element, filename="image.svg"):
        self.root_element = root_element
        self.filename = filename

class Color(object):
    """Class representing colors."""
    def __init__(self, red, green, blue, alpha=None):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    @property
    def rgb(self):
        return (self.red, self.green, self.blue)

    @property
    def rgba(self):
        return (self.red, self.green, self.blue, self.alpha)

    def __str__(self):
        return "#{0:02x}{1:02x}{2:02x}".format(*self.rgb)

    def __eq__(self, other):
        if not issubclass(other.__class__, self.__class__): return False
        return self.rgba == other.rgba

class FillStroke(object):
    """Class for specifying if a change should be applied to fill, stroke or both."""
    def __init__(self, fill=None, stroke=None):
        if fill is None and stroke is None:
            fill = True
            stroke = True
        else:
            if fill is None:
                fill = False
            if stroke is None:
                stroke = False
        self.fill = fill
        self.stroke = stroke

    def __eq__(self, other):
        return self.fill == other.fill and self.stroke == other.stroke

class ChangeColor(CommandBase):
    """Command for changing color."""

    def __init__(self, fill_stroke, to_color, from_color=None):
        self.fill_stroke = fill_stroke
        self.from_color = from_color
        self.to_color = to_color

    def __eq__(self, other):
        return (self.fill_stroke, self.from_color, self.to_color) == (other.fill_stroke, other.from_color, other.to_color)
    def execute(self, execution_context):
        from . import parse
        def parse_color(color_string):
            try:
                return parse.Color.parser().parse_text(parse.join_tokens(color_string.split()),
                                                       eof=True, matchtype="complete").color
            except parse.ParseError:
                return None

        def change_color(node, attribute):
            if attribute in node.keys() and (
                    self.from_color is None
                    or parse_color(node.get(attribute)) == self.from_color):
                node.set(attribute, str(self.to_color))
                opacity_attribute = attribute + "-opacity"
                if self.to_color.alpha is not None and (self.from_color is None
                        or self.from_color.alpha is None
                        or (opacity_attribute in node.keys()
                            and math.round(255 * float(node.get(opacity_attribute)))
                            == self.from_color.alpha)):
                    node.set(opacity_attribute, "{0:.6f}".format(self.to_color.alpha / 255))

        for node in execution_context.selected_nodes:
            for subnode in node.iter():
                if self.fill_stroke.fill:
                    change_color(subnode, "fill")
                if self.fill_stroke.stroke:
                    change_color(subnode, "stroke")

class Length(object):
    """Class representing length."""
    _in_pixels = {
            "mm": 0.0393700787 * DPI,
            "cm": 00.393700787 * DPI,
            "px": 1,
            "pt": 1.25,
            }
    def __init__(self, number, unit="px"):
        self.number = number
        self.unit = unit

    def __eq__(self, other):
        return (self.number, self.unit) == (other.number, other.unit)

    def in_pixels(self):
        """Returns pixel-equivalent of this length."""
        return Length._in_pixels[self.unit] * self.number

"""Class representing displacement.

The difference from Length is only semantical: Length cannot be negative.
The implementation is identical."""
Displacement = Length

class Move(object):
    """Class representing move command."""
    def __init__(self, horizontally, vertically):
        self.horizontally = horizontally
        self.vertically = vertically

    def __eq__(self, other):
        return (self.horizontally, self.vertically) == (other.horizontally, other.vertically)

    def execute(self, execution_context):
        for selection in execution_context.selected_nodes:
            transform = selection.get("transform")
            new_transform = "translate({0},{1}){2}".format(
                    self.horizontally.in_pixels(),
                    self.vertically.in_pixels(),
                    (" " + transform if transform else ""))
            selection.set("transform", new_transform)


class Select(object):
    """Class representing select command."""
    def __init__(self, id):
        self.id = id

    def __eq__(self, other):
        return self.id == other.id

    def execute(self, execution_context):
        new_selection = []
        for selection in execution_context.selected_nodes:
            new_selection.extend(selection.findall(".//*[@id='{0}']".format(self.id)))
        execution_context.selected_nodes = new_selection

class Scale(object):
    """Class representing scale command."""
    def __init__(self, horizontally=1, vertically=1):
        self.horizontally = horizontally
        self.vertically = vertically

    def __eq__(self, other):
        return (self.horizontally, self.vertically) == (other.horizontally, other.vertically)

    def execute(self, execution_context):
        for selection in execution_context.selected_nodes:
            transform = selection.get("transform")
            new_transform = "scale({0},{1}){2}".format(
                    self.horizontally,
                    self.vertically,
                    (" " + transform if transform else ""))
            selection.set("transform", new_transform)

class Remove(object):
    """Class representing remove command."""

    def __eq__(self, other):
        return True

    def execute(self, execution_context):
        parent_map = {}
        for svg_root in execution_context.svg_roots:
            prev = None
            for p in svg_root.root_element.iter():
                for c in p:
                    parent_map[c] = (p, prev)
                    prev = c
                prev = p
        for selection in execution_context.selected_nodes:
            (parent, prev) = parent_map.get(selection, None)
            if parent is not None:
                if prev is not None:
                    prev.tail = selection.tail
                parent.remove(selection)
        execution_context.selected_nodes = []


class ChangeLike(object):
    """Class representing "change like from one_file.svg to another_file.svg" command."""

    class RemoveById(object):
        def __init__(self, id_to_remove):
            self.id_to_remove = id_to_remove

        def execute(self, execution_context):
            context = execution_context.copy()
            context.selected_nodes = [r.root_element for r in context.svg_roots]
            Select(self.id_to_remove).execute(context)
            Remove().execute(context)

    def __init__(self, *change_list):
        self.change_list = change_list

    def __eq__(self, other):
        return self.change_list == other.change_list

    def get_ids(self, filename):
        t = ElementTree.parse(filename)
        return set(e.get("id") for e in t.findall(".//*[@id]") if e.tag != "svg")

    def execute(self, execution_context):
        commands = []
        for i in range(len(self.change_list) - 1):
            from_file = self.change_list[i]
            to_file = self.change_list[i + 1]
            from_ids = self.get_ids(from_file)
            to_ids = self.get_ids(to_file)
            for id in from_ids.difference(to_ids):
                commands.append(ChangeLike.RemoveById(id))

        for command in commands:
            command.execute(execution_context)

