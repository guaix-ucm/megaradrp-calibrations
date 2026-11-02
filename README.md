[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2233591.svg)](https://doi.org/10.5281/zenodo.2233591)

## About ##
This dataset contains calibration files used by the MEGARA data reduction
pipeline.

## Licensing ##

These files are subject to copyright and are licensed under specific conditions
that you must adhere if you wish to redistribute them in whole or in part,
including derived versions.

**Copyright holder:** Universidad Complutense de Madrid

**License:** Creative Commons Attribution 4.0 International

## Description ##

This repository contains the calibration files required for data reduction
following the instructions detailed in the [MEGARA
cookbook](https://guaix-ucm.github.io/megaradrp-cookbook/).

The files are:

* **LinesCatalog**: catalogs of arc lines, in ECSV, named VPH_LAMP.ecsv.
* **ReferenceExtinctionTable**: atmospheric extinction at the Roque de los
  Muchachos Observatory, in ECSV.
* **MasterBPM**: bad pixel masks, in FITS, one for each status of the
  instrument (profile), named with the start of the UUID of the profile:
  * **master_bpm_ca3558e3.fits.gz**: profile ca3558e3-e50d-4bbc-86bd-da50a0998a48,
    images obtained before February 2026
  * **master_bpm_9f3fecbf.fits.gz**: profile 9f3fecbf-376c-47ae-a188-313b7d829104,
    images obtained after February 2026

The catalogs and the extinction table do not depend on the profile.

Each file describes itself with the envelope of numina: the meta of the
ECSV tables and the primary header of the FITS files (keywords NUMENV,
NUMTYPE, NUMFMT, INSTRUME, UUID and INSCONF) give its type, the format of
its contents, the instrument, a unique identifier, the profile (only if
the data depend on it) and the tags used to select it. numina selects the
files by these metadata, whatever their directory, so this dataset
requires a version of numina that reads the envelope; the older versions
use the dataset 2026.2.

## Citation ##

If you use this dataset in your processing of MEGARA data, please cite the
reference given in the Zenodo link below:

https://zenodo.org/record/2233591

For reproducibility purposes, please cite the exact version of the dataset you
are using.

## Main authors ##

Send any comment about this dataset to:
- Nicolás Cardiel <cardiel@ucm.es>
- Sergio Pascual <sergiopr@fis.ucm.es>
