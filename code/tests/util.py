import os
import unittest
from svgplease.main import run

class UsecaseTestLoader(type):
    def __new__(cls, name, bases, dct):
        directory = dct["directory"]
        if directory is not None:
            command_file = os.path.join(os.path.dirname(__file__), "usecases", directory, "command")
            def generate_test(command):
                def test(self):
                    #TODO: actually run the command and test the output
                    pass
                return test
            for i, command in enumerate(open(command_file).readlines()):
                dct["test_command_{0}".format(i)] = generate_test(command)
        return super(UsecaseTestLoader, cls).__new__(cls, name, bases, dct)

class UsecaseTest(unittest.TestCase, metaclass=UsecaseTestLoader):
    """Creates usecase test from one of usecases described in `usecases` directory.

    Each line of the `command` file specifies one test:
        * command from i-th line is run in a directory containing all input$i.* files.
        * the test checks if the generated output$i.* files match expected output$i.* files.
    Usage:
    >>> class SomeTest(UsecaseTest):
    ...     directory = "some_directory"
    """
    directory = None
