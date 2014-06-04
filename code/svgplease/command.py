from xml.etree import ElementTree
import collections
import itertools
import math
import os
import re

"""Global DPI (dots per inch) setting."""
DPI = 120

"""Global verbose setting."""
VERBOSE = False

"""Constant for specifying any node."""
ANY = object()

ElementTree.register_namespace("", "http://www.w3.org/2000/svg")
ElementTree.register_namespace("dc", "http://purl.org/dc/elements/1.1/")
ElementTree.register_namespace("cc", "http://creativecommons.org/ns#")
ElementTree.register_namespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
ElementTree.register_namespace("sodipodi", "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd")
ElementTree.register_namespace("inkscape", "http://www.inkscape.org/namespaces/inkscape")

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

    def select_roots(self):
        self.selected_nodes = [r.root_element.getroot() for r in self.svg_roots]

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

    def __str__(self):
        return str(self.number) + " " + self.unit
    def __repr__(self):
        return "Length(" + str(self.number) + ", '" + self.unit + "')"

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

def explode_style(element):
    """Changes style attribute to set of idividual attributes."""
    style = element.get("style")
    if style is not None:
        for attr in style.split(";"):
            name, value = map(str.strip, attr.split(":"))
            element.set(name, value)
        element.attrib.pop("style")

def explode_style_recursively(element):
    """Recuresively applies explode_style."""
    explode_style(element)
    for c in element:
        explode_style_recursively(c)

class ChangeLike(object):
    """Class representing "change like from one_file.svg to another_file.svg" command."""

    class RemoveById(object):
        def __init__(self, id_to_remove, toplevel=True):
            self.id_to_remove = id_to_remove
            if VERBOSE and toplevel:
                print("Remove <* #{}>".format(id_to_remove))

        def execute(self, execution_context):
            context = execution_context.copy()
            context.select_roots()
            Select(self.id_to_remove).execute(context)
            Remove().execute(context)
            execution_context.selected_nodes = [n for n in execution_context.selected_nodes if n.get("id") != self.id_to_remove]

    class AddTo(object):
        def __init__(self, element, ancestors, toplevel=True):
            self.element = element
            self.ancestors = ancestors
            if VERBOSE and toplevel:
                e = element
                a = ancestors[0][0]
                print("Add <{} #{}> to <{} #{}>".format(e.tag, e.get("id"), a.tag, a.get("id")))

        def addTo(self, root):
            element = root
            for i, (ancestor, idx) in enumerate(self.ancestors):
                if i == len(self.ancestors) - 1:
                    break
                ancestor_id = ancestor.get("id")
                if ancestor_id is None:
                    continue
                e = root.find(".//*[@id='{0}']".format(ancestor_id))
                if e is not None:
                    element = e
                    break

            previous_sibling_ids = [c.get("id") for c in ancestor[:idx] if c.get("id")]
            element_children_idx = {c.get("id"): i for i, c in enumerate(element) if c.get("id")}

            insert_idx = 0
            for sibling_id in reversed(previous_sibling_ids):
                child_idx = element_children_idx.get(sibling_id)
                if child_idx is not None:
                    insert_idx = child_idx + 1
                    break
            element.insert(insert_idx, self.element)

        def execute(self, execution_context):
            for svg_root in execution_context.svg_roots:
                self.addTo(svg_root.root_element.getroot())

    class Move(object):
        def __init__(self, id_to_move, ancestors, toplevel=True):
            self.id_to_move = id_to_move
            self.ancestors = ancestors
            if VERBOSE and toplevel:
                a = ancestors[0][0]
                print("Move <* #{}> to <{} #{}>".format(id_to_move, a.tag, a.get("id")))

        def execute(self, execution_context):
            context = execution_context.copy()
            context.select_roots()
            for svg_root, root in zip(context.svg_roots, context.selected_nodes):
                element = root.find(".//*[@id='{0}']".format(self.id_to_move))
                if element is None:
                    continue
                execution_context = ExecutionContext()
                execution_context.svg_roots = [svg_root]
                execution_context.selected_nodes = [root]
                ChangeLike.RemoveById(self.id_to_move, False).execute(execution_context)
                ChangeLike.AddTo(element, self.ancestors, False).execute(execution_context)

    class SetAttribute(object):
        def __init__(self, element, attribute_name, attribute_value, replace=ANY, recursively=False, toplevel=True):
            self.element = element
            self.attribute_name = attribute_name
            self.attribute_value = attribute_value
            self.replace = replace
            self.recursively = recursively
            if toplevel:
                self.explain()

        def explain(self):
            if VERBOSE:
                print("Set attribute (recursively? {}, replace? {}): <* #{} {}={}>".format(
                            self.recursively, self.replace, self.element.get("id"),
                            self.attribute_name, self.attribute_value))

        def execute(self, execution_context):
            context = execution_context.copy()
            context.select_roots()
            for root in context.selected_nodes:
                change_elements = collections.deque([self.element])
                while change_elements:
                    change_element = change_elements.popleft()
                    element_id = change_element.get("id")
                    element_to_change = None if element_id is None else root.find(".//*[@id='{0}']".format(element_id))
                    if element_id is None or element_to_change is None:
                        change_elements.extend(list(change_element))
                        continue

                    elements = collections.deque([element_to_change])
                    while elements:
                        element = elements.popleft()
                        value = element.get(self.attribute_name)
                        if (not self.recursively or len(element) == 0) and self.replace in (ANY, value):
                            if self.attribute_value is None:
                                if self.attribute_name in element.attrib:
                                    element.attrib.pop(self.attribute_name)
                            else:
                                element.set(self.attribute_name, self.attribute_value)
                        if self.recursively:
                            for child in element:
                                elements.append(child)

    def __init__(self, *change_list):
        self.change_list = change_list

    def __eq__(self, other):
        return self.change_list == other.change_list

    def get_ids(self, root):
        return {e.get("id"): e for e in root.findall(".//*[@id]") if e.tag != "svg" and e.get("id")}

    def find_ancestors(self, root, ids):
        results = {}
        stack = []

        def dfs(elem):
            id = elem.get("id")
            if id in ids:
                results[id] = list(reversed(stack))
            for i, c in enumerate(elem):
                stack.append((elem, i))
                dfs(c)
                stack.pop()
        dfs(root)
        return results

    def generalizeSetAttribute(self, root, previous_elements, commands):

        def generalize(element, attr, command_dict): #TODO: remove attribute
            element_id = element.get("id")
            value = element.get(attr)
            previous_value = None if element_id is None or element_id not in previous_elements else previous_elements[element_id].get(attr)

            replace = collections.defaultdict(set)
            commands = []
            is_leaf = True
            for child in element:
                is_leaf = False
                child_commands, child_replace = generalize(child, attr, command_dict)
                for p, v in child_replace.items():
                    replace[p].update(v)
                commands.extend(child_commands)
            if is_leaf:
                replace[previous_value].add(value)

            leaf_values = set()
            for values in replace.values():
                leaf_values.update(values)
            update_values = set()
            update_keys = set()
            for command in commands:
                update_values.add(command.attribute_value)
                update_keys.add(command.replace)
            for key in update_keys:
                update_values.update(replace[key])
            update_values.update(replace[ANY])
            if len(leaf_values) == 1 or (len(update_values) == 1 and len(update_keys) == 1):
                replace_value = ANY if len(update_keys) != 1 else list(update_keys)[0]
                recursive = [c for c in commands if c.recursively]
                commands = [c for c in commands if not c.recursively]
                if recursive:
                    set_value = list(update_values)[0]
                    commands += [ChangeLike.SetAttribute(element, attr, set_value,
                        replace=replace_value, recursively=True, toplevel=False)]
            command = []
            if element_id is not None and element_id in command_dict:
                command = [command_dict[element_id]]
                if is_leaf:
                    command[0].recursively = True
            return commands + command, replace

        def attribute_name(set_attribute):
            return set_attribute.attribute_name

        result = []

        for attribute, cmds in itertools.groupby(sorted(commands, key=attribute_name), attribute_name):
            change_commands = generalize(root, attribute, {c.element.get("id") : c for c in cmds})[0]
            for command in change_commands:
                command.explain()
                result.append(command)

        return result

    def execute(self, execution_context):
        for svg_root in execution_context.svg_roots:
            explode_style_recursively(svg_root.root_element.getroot())
        commands = []
        for i in range(len(self.change_list) - 1):
            from_file = self.change_list[i]
            to_file = self.change_list[i + 1]
            from_root = ElementTree.parse(from_file).getroot()
            to_root = ElementTree.parse(to_file).getroot()
            explode_style_recursively(from_root)
            explode_style_recursively(to_root)
            from_elements = self.get_ids(from_root)
            to_elements = self.get_ids(to_root)

            for id in set(from_elements.keys()).difference(to_elements.keys()):
                commands.append(ChangeLike.RemoveById(id))

            elements_to_add = set(set(to_elements.keys()).difference(from_elements.keys()))
            ancestors = self.find_ancestors(to_root, elements_to_add)
            for id in elements_to_add:
                commands.append(ChangeLike.AddTo(to_elements[id], ancestors[id]))

            elements_to_move = set(from_elements.keys()).intersection(to_elements.keys())
            from_ancestors = self.find_ancestors(from_root, elements_to_move)
            to_ancestors = self.find_ancestors(to_root, elements_to_move)
            for id in elements_to_move:
                (fa, _), (ta, _) = from_ancestors[id][0], to_ancestors[id][0]
                if fa.get("id") != ta.get("id"):
                    commands.append(ChangeLike.Move(id, to_ancestors[id]))

            elements_to_change = set(from_elements.keys()).intersection(to_elements.keys())
            change_commands = []
            for id in elements_to_change:
                for attr in to_elements[id].attrib:
                    fv, tv = from_elements[id].get(attr), to_elements[id].get(attr)
                    if fv != tv:
                        change_commands.append(ChangeLike.SetAttribute(
                            to_elements[id], attr, to_elements[id].get(attr),
                            replace=from_elements[id].get(attr), toplevel=False))
            commands.extend(self.generalizeSetAttribute(to_root, from_elements, change_commands))

        for command in commands:
            command.execute(execution_context)

class ChangeText(object):
    """Class representing "change text to 'foo bar'" command."""

    def __init__(self, text):
        self.text = text

    def __eq__(self, other):
        return self.text == other.text

    def __str__(self):
        return "ChangeText('" + self.text + "')"

    __repr__ = __str__

    def execute(self, execution_context):
        for node in execution_context.selected_nodes:
            for n in node.iter():
                if n.tag.endswith("text") or n.tag.endswith("flowPara"):
                    n.text = self.text

class Page(object):
    """Class representing page dimensions."""

    """Supported predefined page sizes."""
    PAGE_SIZE = {
            "a3": (Length(297, "mm"), Length(420, "mm")),
            "a4": (Length(210, "mm"), Length(297, "mm")),
            "a5": (Length(148, "mm"), Length(210, "mm")),
        }

    def __init__(self, *args):
        """
        If single argument is given it is considered to be a predefined name (a3, a4, a5).
        If two arguments are given they are supposed to be the dimensions (width, height).
        """
        if len(args) == 1:
            wh = Page.PAGE_SIZE[args[0]]
        if len(args) == 2:
            wh = args
        self.width, self.height = wh

    def __eq__(self, other):
        return (self.width, self.height) == (other.width, other.height)

    def __str__(self):
        return "Page(" + str(self.width) + ", " + str(self.height) + ")"

    def __repr__(self):
        return "Page(" + repr(self.width) + ", " + repr(self.height) + ")"

class Tile(object):
    """Class represnting "tile" command."""

    def __init__(self, page, fill):
        self.page = page
        self.fill = fill

    def __eq__(self, other):
        return (self.page, self.fill) == (other.page, other.fill)
