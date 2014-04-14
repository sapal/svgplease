import unittest
from . import util

class OpenAndSave(util.UsecaseTest):
    directory = "open_and_save"

class SetColor(util.UsecaseTest):
    directory = "set_color"

class MoveRelative(util.UsecaseTest):
    directory = "move_relative"
    failed_directory = "/tmp/failed"
