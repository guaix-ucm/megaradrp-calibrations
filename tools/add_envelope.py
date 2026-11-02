"""Add the envelope of numina to the calibration files

The envelope says what a file is and in which format (see
numina.store.envelope). The files keep their other metadata:

ECSV (lines catalogs, extinction tables)
    ``envelope: 1`` is added at the start of the meta, and ``format: 2``
    after the type. The text of the file is edited, not rewritten with
    astropy, to keep the lines of data that are commented out.
FITS (bad pixel masks)
    The keywords NUMENV = 1, NUMTYPE (the type, the name of the
    directory of the file) and NUMFMT = 1 are added to the primary header,
    and the checksums are updated. INSTRUME, UUID and INSCONF are
    already there.

Files that already have an envelope are left as they are.

Usage: python tools/add_envelope.py FILE [FILE ...]
"""

import argparse
import pathlib

from astropy.io import fits

ENVELOPE = 1
#: Format of the contents of each container
FORMATS = {"ecsv": 2, "fits": 1}


def add_ecsv(path):
    """Add envelope and format to the meta of an ECSV file, return False if it had them"""
    lines = path.read_text().splitlines()
    if "# - {envelope: 1}" in lines:
        return False
    try:
        start = lines.index("# meta: !!omap")
        itype = next(i for i in range(start, len(lines)) if lines[i].startswith("# - {type: "))
    except (ValueError, StopIteration):
        raise ValueError(f"{path}: the meta has no type") from None
    lines.insert(itype + 1, f"# - {{format: {FORMATS['ecsv']}}}")
    lines.insert(start + 1, f"# - {{envelope: {ENVELOPE}}}")
    path.write_text("\n".join(lines) + "\n")
    return True


def add_fits(path):
    """Add NUMENV, NUMTYPE and NUMFMT to the primary header, return False if it had them"""
    # Written to another file, the data are read from path while writing
    tmp = path.with_name(f".{path.name}.tmp{''.join(path.suffixes)}")
    with fits.open(path, do_not_scale_image_data=True) as hdul:
        header = hdul[0].header
        if "NUMENV" in header:
            return False
        for keyword in ["INSTRUME", "UUID", "INSCONF"]:
            if keyword not in header:
                raise ValueError(f"{path}: the primary header has no {keyword}")
        header["NUMENV"] = (ENVELOPE, "Version of the numina envelope")
        header["NUMTYPE"] = (path.parent.name, "Product type")
        header["NUMFMT"] = (FORMATS["fits"], "Format of the contents of the type")
        hdul.writeto(tmp, checksum=True)
    tmp.replace(path)
    return True


def main(args=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+", type=pathlib.Path)
    args = parser.parse_args(args)
    for path in args.files:
        if path.name.endswith(".ecsv"):
            changed = add_ecsv(path)
        elif path.name.endswith((".fits", ".fits.gz")):
            changed = add_fits(path)
        else:
            raise ValueError(f"{path}: not an ECSV or FITS file")
        print(f"{path}: {'envelope added' if changed else 'already has an envelope'}")


if __name__ == "__main__":
    main()
