"""Allow ``python -m bias_aperture`` to launch the CLI."""

import sys

from bias_aperture.cli import main

if __name__ == "__main__":
    sys.exit(main())
