"""
Download and extract BEDMAP2 data as needed.
"""
import os.path as op
import zipfile

import wget

# the URL where we download BEDMAP2
BEDMAP2_URL = "https://secure.antarctica.ac.uk/data/bedmap2/bedmap2_tiff.zip"

# the directory where we store the data
DATA_DIR = op.join(op.dirname(op.dirname(__file__)), "data")


def data_exists() -> bool:
    """
    Check if the BEDMAP2 data exists.

    Returns
    -------
    exists: bool
        If True, the BEDMAP2 data exists on the local disk.
    """
    return op.exists(f"{op.join(DATA_DIR, *('bedmap2_tiff', 'bedmap2_bed.tif'))}")


def download_data() -> bool:
    """
    Download the BEDMAP2 dataset and replace the existing files (if present).

    Returns
    -------
    success: bool
        A boolean indicating a succesful download.
    """

    # construct the filename where we store the data
    filename = f"{DATA_DIR}/bedmap2_tiff.zip"

    # check if the zip file is not present
    if not op.exists(filename):
        # and download the data
        wget.download(BEDMAP2_URL, filename)
    else:
        # the file is already downloaded
        print("BEDMAP2 is already downloaded.")

    # now expand the zip file
    with zipfile.ZipFile(filename, "r") as zf:
        # extract all the files into the data directory
        zf.extractall(DATA_DIR)

    # check that the data now exists
    return data_exists()
