from contextlib import contextmanager
import glob
import os
import shutil
import svgplease.main
import unittest
import tempfile

TEST_DATA = os.path.join(os.path.dirname(__file__), "testdata")

@contextmanager
def TestDirectory(*files):
    """Generates temporary directory and copies given files to it."""
    with tempfile.TemporaryDirectory(prefix="svgplease-test") as tempdirname:
        for f in files:
            shutil.copy(f, tempdirname)
        yield tempdirname

class UsecaseTestLoader(type):
    def __new__(cls, name, bases, dct):
        if dct["directory"] is not None:
            directory = os.path.join(os.path.dirname(__file__), "usecases", dct["directory"])
            command_file = os.path.join(directory, "command")
            def generate_test(command, idx):
                def test(self):
                    input_files = glob.glob(os.path.join(directory, "input{0}.*".format(idx)))
                    expected_output_files = glob.glob(os.path.join(directory, "output{0}.*".format(idx)))
                    with TestDirectory(*input_files) as tempdirname:
                        svgplease.main.run("test", command.split())
                        for expected_output_file in expected_output_files:
                            output_file = os.path.join(
                                    tempdirname,
                                    os.path.basename(expected_output_file))
                            self.assertSameSVG(output_file, expected_output_file)
                return test
            for i, command in enumerate(open(command_file).readlines()):
                dct["test_command_{0}".format(i)] = generate_test(command, i)
        return super(UsecaseTestLoader, cls).__new__(cls, name, bases, dct)

class UsecaseTest(unittest.TestCase, metaclass=UsecaseTestLoader):
    """Creates usecase test from one of usecases described in `usecases` directory.

    Each line of the `command` file specifies one test:
        * command from i-th line is run in a directory containing all input$i.* files.
        * the test checks if the generated output$i.* files match expected output$i.* files.
    Note that the commands should be space-separated (i.e. no filenames with spaces).
    Usage:
    >>> class SomeTest(UsecaseTest):
    ...     directory = "some_directory"
    """
    directory = None
    def assertSameSVG(self, output_file, expected_output_file):
        #TODO: actually check file content
        self.assertTrue(os.path.isfile(output_file))
