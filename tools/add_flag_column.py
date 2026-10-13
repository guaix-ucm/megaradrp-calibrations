#
# Copyright 2026 Universidad Complutense de Madrid
#
# This file is part of megaradrp-calibrations
#
# License: Creative Commons Attribution 4.0 International
#

"""Insert a second column with 1 in the data lines of two-column lines catalogs

Used to convert the catalogs of two columns (wavelength, intensity) to the
format of three columns (wavelength, flag, intensity) of the other catalogs:

    python tools/add_flag_column.py FILE.lis ...

The data lines can be disabled with '#'. The separator of the first two
columns, the inline comments and the line endings are kept.
"""

import re
import sys

NUMBER = rb"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
DATA = re.compile(rb"^(\s*#?\s*)(\d+(?:\.\d*)?)(\s+)(" + NUMBER + rb")(.*)$")

for path in sys.argv[1:]:
    with open(path, "rb") as fd:
        lines = fd.read().split(b"\n")
    out = []
    changed = 0
    for line in lines:
        ending = b"\r" if line.endswith(b"\r") else b""
        body = line[:-1] if ending else line
        match = DATA.match(body)
        if match:
            prefix, wave, sep, second, rest = match.groups()
            # the rest is empty or an inline comment, not a third column;
            # in a disabled line, all the rest is a comment
            disabled = b"#" in prefix
            if not disabled and rest.strip() and not rest.lstrip().startswith(b"#"):
                sys.exit(f"{path}: unexpected line {body!r}")
            body = prefix + wave + sep + b"1" + sep + second + rest
            changed += 1
        out.append(body + ending)
    with open(path, "wb") as fd:
        fd.write(b"\n".join(out))
    print(f"{changed:3d} lines  {path}")
