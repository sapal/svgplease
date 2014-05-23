import unittest
from . import util

class OpenAndSave(util.UsecaseTest):
    directory = "open_and_save"

class SetColor(util.UsecaseTest):
    directory = "set_color"

class MoveRelative(util.UsecaseTest):
    directory = "move_relative"

class Scale(util.UsecaseTest):
    directory = "scale"

class Remove(util.UsecaseTest):
    directory = "remove"

class ChangeLike(util.UsecaseTest):
    directory = "change_like"
    failed_directory = "/tmp/failed"
