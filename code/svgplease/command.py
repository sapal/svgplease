class OpenSaveBase(object):
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
    pass

class Save(OpenSaveBase):
    """Command for saving files"""
    pass
