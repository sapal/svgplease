import unittest
import sys

all_testmodules = ["test_usecases"]

def suite():
  this_module = sys.modules[__name__]
  for module in all_testmodules:
    setattr(this_module, module, __import__(module, globals(), locals(), [], 1))
  return unittest.defaultTestLoader.loadTestsFromNames(all_testmodules, this_module)

all_tests = suite()
