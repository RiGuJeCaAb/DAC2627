import sys

from .cli import main

try:
    sys.exit(main())
except BrokenPipeError:  # ex.: dac lint | head
    sys.exit(0)
