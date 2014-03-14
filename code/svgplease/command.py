from xml.etree import ElementTree

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

class Save(OpenSaveBase):
    """Command for saving files"""
    pass

class ExecutionContext(object):
    """Class for storing execution context for the commands.

    It has the following fields:
        - svg_roots - stores root elements for all opened/generated svg files
    """

    def __init__(self):
        self.svg_roots = []

class SVGRoot(object):
    """Class representing the root node of SVG file."""
    def __init__(self, root_element, filename="image.svg"):
        self.root_element = root_element
        self.filename = filename
