"""Convert the lines catalogs of three columns (.lis) to ECSV

The columns are wavelength, flag and intensity, with the comment of each
line in a fourth column. The lines that are commented out in the
catalog are kept, commented out, in the same position (the ECSV reader
of astropy skips them).

The metadata of the catalog is stored in the header: instrument, type,
profile, a new uuid and the tags (vph and speclamp), taken from the
path PROFILE/LinesCatalog/LAMP/VPH/FILE.lis. The text of the header of
the catalog is stored in description, and the URLs in references, each
with the text that introduces it as a note.

Usage: python tools/lis_to_ecsv.py FILE.lis [FILE.lis ...]

Each FILE.lis is replaced by FILE.ecsv (use git mv first to keep the
history).
"""

import argparse
import io
import pathlib
import re
import uuid

import numpy
from astropy.table import Table
import astropy.units as u

# A line of data, possibly commented out: wavelength flag intensity
NUMBER = r"[-+]?\d+\.?\d*(?:[eE][-+]?\d+)?"
DATA = re.compile(rf"^#?\s*(\d+\.?\d*)\s+({NUMBER})\s+({NUMBER})\s*(?:#\s*(.*))?$")
# The start of a line of data commented out, with or without comment
COMMENTED_DATA = re.compile(r"^#\s*\d+\.\d*\s+\S+\s+\S+")
SEPARATOR = re.compile(r"^#\s*-+\s*$")
COLUMN = re.compile(r"^#\s*Column #\d+:")
OLD_UUID = re.compile(r"^#\s*uuid:", re.IGNORECASE)
AR_REMOVED = re.compile(r"^\(Ar lines from that list have been removed\)\.?$")
URL = re.compile(r"^(https?|ftp)://")

DESCRIPTIONS = {
    "wavelength": "Wavelength of the line",
    "flag": "1: bright enough subsample, used in the initial calibration; 0: faint subsample",
    "intensity": "Relative intensity (NIST)",
    "comment": "Comment",
}


def convert(path):
    path = pathlib.Path(path)
    parts = path.parts
    idx = parts.index("LinesCatalog")
    profile = parts[idx - 1]
    lamp, vph = parts[idx + 1], parts[idx + 2]

    lines = path.read_text().splitlines()
    header = []
    body = []
    in_header = True
    for line in lines:
        if in_header and line.startswith("#") and not COMMENTED_DATA.match(line):
            header.append(line)
        else:
            in_header = False
            if line.strip():
                body.append(line)
    # The comments after the last separator of the header ("overlap
    # with LR-B") refer to the lines that follow them
    structural = [i for i, line in enumerate(header) if SEPARATOR.match(line) or COLUMN.match(line) or OLD_UUID.match(line)]
    if structural:
        last = structural[-1] + 1
        body = header[last:] + body
        header = header[:last]

    # The first text lines of the header, before those that introduce
    # a reference, are the description
    texts = []
    for line in header:
        if SEPARATOR.match(line) or COLUMN.match(line) or OLD_UUID.match(line):
            continue
        text = line.lstrip("#").strip()
        if text:
            texts.append(text.replace("extrated", "extracted"))
    nversion = 0
    for text in texts:
        if text.endswith("version"):
            nversion += 1
        else:
            break
    # The VPH of the version is that of the catalog (MR-B said LR-B)
    description = " ".join(re.sub(r"^\S+ Nico's version$", f"{vph} Nico's version", text) for text in texts[:nversion])
    references = []
    pending = []
    rest = []
    last_was_url = False
    for text in texts[nversion:]:
        if URL.match(text):
            note = " ".join(pending).rstrip(":").strip()
            if not note and references and last_was_url:
                # Several URLs after the same text
                note = references[-1].get("note", "")
            reference = {"note": note, "url": text} if note else {"url": text}
            references.append(reference)
            pending = []
            last_was_url = True
            continue
        elif text.startswith("(") and references and not pending:
            # A remark on the previous reference
            if AR_REMOVED.match(text):
                text = "this list, without its Ar lines"
            references[-1]["note"] = f"{references[-1].get('note', '')} {text}".strip()
        else:
            pending.append(text)
        last_was_url = False
    rest.extend(pending)
    if rest:
        description = " ".join([description] + rest).strip()

    rows = []
    commented = []
    for line in body:
        match = DATA.match(line)
        if line.startswith("#"):
            # Commented out lines, kept before the row that follows them
            commented.append((len(rows), line))
        elif match:
            wave, flag, intensity, comment = match.groups()
            if float(flag) not in (0, 1):
                raise ValueError(f"{path}: flag is not 0 or 1 in line {line!r}")
            rows.append((float(wave), int(float(flag)), float(intensity), (comment or "").strip()))
        else:
            raise ValueError(f"{path}: unexpected line {line!r}")

    table = Table(rows=rows, names=["wavelength", "flag", "intensity", "comment"])
    table["wavelength"].unit = u.AA
    intensity = table["intensity"]
    if numpy.all(intensity == numpy.round(intensity)):
        table["intensity"] = intensity.astype("int64")
    for name, desc in DESCRIPTIONS.items():
        table[name].description = desc
    table.meta["instrument"] = "MEGARA"
    table.meta["type"] = "LinesCatalog"
    table.meta["profile"] = profile
    table.meta["uuid"] = str(uuid.uuid4())
    table.meta["tags"] = {"speclamp": lamp, "vph": vph}
    if description:
        table.meta["description"] = description
    if references:
        table.meta["references"] = references

    out = io.StringIO()
    table.write(out, format="ascii.ecsv")
    written = out.getvalue().splitlines()
    nhead = len(written) - len(rows)
    result = written[:nhead]
    data = written[nhead:]
    pos = 0
    for irow, row in enumerate(data):
        while pos < len(commented) and commented[pos][0] == irow:
            result.append(commented[pos][1])
            pos += 1
        result.append(row)
    result.extend(line for _, line in commented[pos:])

    dest = path.with_suffix(".ecsv")
    dest.write_text("\n".join(result) + "\n")
    return dest


def main(args=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+")
    args = parser.parse_args(args)
    for name in args.files:
        print(convert(name))


if __name__ == "__main__":
    main()
