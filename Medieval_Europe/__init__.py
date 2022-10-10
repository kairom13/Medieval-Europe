import sys
import os


def get_parent_path():
    if getattr(sys, "frozen", False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)

        return os.path.join(datadir, 'lib/Medieval_Europe/')

    else:
        # The application is not frozen
        return os.path.dirname(__file__)
