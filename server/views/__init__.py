'''Helper to make importing views easier'''

from os.path import dirname, basename, isfile, join
import glob

MODULES = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [basename(f)[:-3] for f in MODULES if isfile(f) and not f.endswith('__init__.py')]

# pylint: disable=import-self, wrong-import-position
from . import *
