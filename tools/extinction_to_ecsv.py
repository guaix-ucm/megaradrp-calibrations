"""Convert the reference extinction tables to ECSV

The columns are wavelength (Angstrom) and extinction (magnitudes per
unit airmass).

The metadata of the table is stored in the header: instrument, type,
profile (from the path PROFILE/ReferenceExtinctionTable/FILE), a new
uuid, empty tags, the description of the table and its reference.

Usage: python tools/extinction_to_ecsv.py FILE [FILE ...]

Each FILE is replaced by FILE.ecsv (use git mv first to keep the
history).
"""

import argparse
import pathlib
import uuid

import numpy
from astropy.table import Table
import astropy.units as u

DESCRIPTION = "Atmospheric extinction at the Roque de los Muchachos Observatory, La Palma"
REFERENCE = {
    "note": "Table 1 in RGO/La Palma technical note no. 31",
    "url": "https://www.ing.iac.es/Astronomy/observing/manuals/ps/tech_notes/tn031.pdf",
}


def convert(path):
    path = pathlib.Path(path)
    parts = path.parts
    idx = parts.index("ReferenceExtinctionTable")
    profile = parts[idx - 1]

    text = path.read_text()
    # The table is checked to be the one described here
    if "RGO/La Palma technical note no. 31" not in text:
        raise ValueError(f"{path}: unexpected extinction table")
    data = numpy.loadtxt(path.open(), ndmin=2)
    if data.shape[1] != 2:
        raise ValueError(f"{path}: expected two columns")

    table = Table(data, names=["wavelength", "extinction"])
    table["wavelength"].unit = u.AA
    table["wavelength"].description = "Wavelength"
    table["extinction"].unit = u.mag
    table["extinction"].description = "Extinction coefficient, in magnitudes per unit airmass"
    table.meta["instrument"] = "MEGARA"
    table.meta["type"] = "ReferenceExtinctionTable"
    table.meta["profile"] = profile
    table.meta["uuid"] = str(uuid.uuid4())
    table.meta["tags"] = {}
    table.meta["description"] = DESCRIPTION
    table.meta["references"] = [REFERENCE]

    dest = path.with_suffix(".ecsv")
    table.write(dest, format="ascii.ecsv", overwrite=True)
    return dest


def main(args=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+")
    args = parser.parse_args(args)
    for name in args.files:
        print(convert(name))


if __name__ == "__main__":
    main()
