class Open(object):
    """Command for opening files"""
    def __init__(self, *filenames):
        self.filenames = filenames

    def __eq__(self, other):
        return self.filenames == other.filenames

    #TODO: __hash__ ?

class Save(object):
    """Command for saving files"""
    def __init__(self, *filenames):
        self.filenames = filenames

    def __eq__(self, other):
        return self.filenames == other.filenames

    #TODO: __hash__ ?

