import os
from os.path import abspath, dirname, join
from typing import Any

import numpy as np
import numpy.ma as ma
import rasterio
from cachetools import cached

import bedmap2.downloader as downloader
import bedmap2.transform as transform

# the default directory if BEDMAP_DATA is not defined
default_bedmap_dir = join(
    dirname(dirname(abspath(__file__))), *("data", "bedmap2_tiff")
)

# if BEDMAP_DATA is defined, use that - otherwise use the default directory.
bedmap_dir = os.environ.get("BEDMAP2_DATA", default_bedmap_dir)


@cached(cache={})
def load_data(name: str) -> ma.masked_array:
    """
    Load a BEDMAP data file specified by `name` in the BEDMAP data directory.

    The reults of this function are cached so calling this function with
    the same argument will return the already-loaded data file.

    Parameters
    ----------
    name: str
        The name of the BEDMAP data file to load.

    Returns
    -------
    data: np.ndarray
        The loaded datafile as a numpy masked array.
    """

    # if the data is not download it, download it
    if not downloader.data_exists():
        downloader.download_data()

    # check that we have a valid name
    if name not in [
        "bed",
        "coverage",
        "grounded_bed_uncertainty",
        "rockmask",
        "icemask_grounded_and_shelves",
        "lakemask_vostok",
        "surface",
        "thickness",
        "thickness_uncertainty_5km",
        "gl04c_geiod_to_WGS84",
    ]:
        raise ValueError(f"{name} is not a valid BEDMAP layer")

    # we have a valid name for the data

    # get the full filename - prepend bedmap2_ to most filenames
    if name != "gl04c_geiod_to_WGS84":
        name = f"bedmap2_{name}.tif"
    else:
        name = f"{name}.tif"

    # load the file
    dataset = rasterio.open(join(bedmap_dir, name))

    # get the value used for nodata
    nodata = dataset.meta["nodata"]

    # and return the data layer from the dataset
    return ma.masked_equal(dataset.read(1), nodata)


def dataset(
    lat: np.ndarray, lon: np.ndarray, name: str, mode: str = "latlon"
) -> np.ndarray:
    """
    Return the value of a given dataset at a specified set
    of `latitude` and `longitudes` or polar stereographic coordinates.

    if `mode` is `latlon`, the input arguments are treated as latitude and
    longitude in decimal degrees. If `mode` is `xy`, arguments are treated
    as (x, y) coordinates (in meters) in the South Polar Stereographic Projection.

    Parameters
    ----------
    lat or x: np.ndarray
        The latitude of each point in degrees.
    lon or y: np.ndarray
        The longitude of each point in degrees.
    name: str
        The name of the dataset to load.
    mode: str
        Whether the coordinates are 'latlon' or 'xy' coordinates.

    Returns
    -------
    value: np.ndarray
        The values of the dataset at each location.
    """
    # check if we have to convert
    if mode == "latlon":
        # get x and y indices into coordinates
        ix, iy = transform.latlon_to_index(lat, lon)
    elif mode == "xy":
        # convert x,y to indices
        ix, iy = transform.xy_to_index(lat, lon)
    else:
        raise ValueError(f"{mode} is an invalid dataset access mode.")

    # make sure the data is loaded - this is cached.
    data = load_data(name)

    # and return the corresponding data indices
    return data[ix, iy]


def bed(*args: Any, **kwargs: Any) -> np.ndarray:
    """
    Sample the bed height in meters relative to the GL04C geoid.

    Parameters
    ----------
    lat or x: np.ndarray
        The latitude of each point in degrees.
    lon or y: np.ndarray
        The longitude of each point in degrees.
    mode: str
        Whether the coordinates are 'latlon' or 'xy' coordinates.

    Returns
    -------
    bed height: np.ndarray
        The bed height in meters relative to the GL04C geoid.
    """
    return dataset(*args, name="bed", **kwargs)  # type: ignore


def surface(*args: Any, **kwargs: Any) -> np.ndarray:
    """
    Sample the surface height in meters relative to the GL04C geoid.

    Parameters
    ----------
    lat or x: np.ndarray
        The latitude of each point in degrees or PS coordinate in meters.
    lon or y: np.ndarray
        The longitude of each point in degrees or PS coordinate in meters.
    mode: str
        Whether the coordinates are 'latlon' or 'xy' coordinates.

    Returns
    -------
    surface height: np.ndarray
        The surface height in meters relative to the GL04C geoid.
    """
    return dataset(*args, name="surface", **kwargs)  # type: ignore


def thickness(*args: Any, **kwargs: Any) -> np.ndarray:
    """
    Sample the ice thickness in meters.

    Parameters
    ----------
    lat or x: np.ndarray
        The latitude of each point in degrees or PS coordinate in meters.
    lon or y: np.ndarray
        The longitude of each point in degrees or PS coordinate in meters.
    mode: str
        Whether the coordinates are 'latlon' or 'xy' coordinates.

    Returns
    -------
    ice thickness: np.ndarray
        The ice thickness in meters.
    """
    return dataset(*args, name="thickness", **kwargs)  # type: ignore


def rockmask(*args: Any, **kwargs: Any) -> np.ndarray:
    """
    Sample the rock mask at each point - if 1, there is rock
    present at that location.

    Parameters
    ----------
    lat or x: np.ndarray
        The latitude of each point in degrees or PS coordinate in meters.
    lon or y: np.ndarray
        The longitude of each point in degrees or PS coordinate in meters.
    mode: str
        Whether the coordinates are 'latlon' or 'xy' coordinates.

    Returns
    -------
    rock mask: np.ndarray
        The rock mask at each location.
    """
    return dataset(*args, name="rockmask", **kwargs)  # type: ignore


def bed_uncertainty(*args: Any, **kwargs: Any) -> np.ndarray:
    """
    Sample the bed uncertainty in meters at each point.

    Parameters
    ----------
    lat or x: np.ndarray
        The latitude of each point in degrees or PS coordinate in meters.
    lon or y: np.ndarray
        The longitude of each point in degrees or PS coordinate in meters.
    mode: str
        Whether the coordinates are 'latlon' or 'xy' coordinates.

    Returns
    -------
    bed uncertainty: np.ndarray
        The bed uncertainty in meters.
    """
    return dataset(*args, name="bed_uncertainty", **kwargs)  # type: ignore


def icemask(*args: Any, **kwargs: Any) -> np.ndarray:
    """
    Sample the icemask - this returns whether the
    point is grounded or an ice shelf.

    Parameters
    ----------
    lat or x: np.ndarray
        The latitude of each point in degrees.
    lon or y: np.ndarray
        The longitude of each point in degrees.
    mode: str
        Whether the coordinates are 'latlon' or 'xy' coordinates.

    Returns
    -------
    bed uncertainty: np.ndarray
        The bed uncertainty in meters.
    """
    return dataset(*args, name="icemask_grounded_and_shelves", **kwargs)  # type: ignore


def gl04c_to_wgs84(*args: Any, **kwargs: Any) -> np.ndarray:
    """
    Add this array to values in meters to convert from
    GL04C to WGS84.

    Parameters
    ----------
    lat or x: np.ndarray
        The latitude of each point in degrees or PS coordinate in meters.
    lon or y: np.ndarray
        The longitude of each point in degrees or PS coordinate in meters.
    mode: str
        Whether the coordinates are 'latlon' or 'xy' coordinates.

    Returns
    -------
    conversion: np.ndarray
        The height to convert a value from GL04C to WGS84.
    """
    return dataset(*args, name="gl04c_geiod_to_WGS84", **kwargs)  # type: ignore
