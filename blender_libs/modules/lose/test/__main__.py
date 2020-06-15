import sys
from .unittests import *
from . import __version__

if '--version' in sys.argv:
	print (__version__)

elif __name__ == '__main__':
	u.main()
