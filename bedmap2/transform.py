from typing import Tuple

import numpy as np
import numpy.ma as ma

# the Earth eccentricity
e = 0.081816153

# the Earth major axis (km)
a = 6378.273

# the number of columns in the BEDMAP dataset (1km resolution)
ncols = 6667

# the number of rows in the BEDMAP dataset (1km resolution)
nrows = 6667

# the minimum value of woth the x and y coordinate (km) (1km resolution)
psmin = -3333.5

# the maximum value of both the x and y coordinates (km) (1km resolution)
psmax = 3333.5


def xy_to_index(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert an array of x and y (in polar stereographic) coordinates
    (in meters) into BEDMAP2 1km data indices.

    Parameters
    ----------
    x: np.ndarray
        A N-length Numpy array of x-coordinates (m).
    y: np.ndarray
        A N-length Numpy array of y-coordinates (m).

    Returns
    -------
    ix, iy: np.ndarray
        The (ix, iy) indices into the BEDMAP2 dataset.
    """

    # and get these are indices - since BEDMAP has a resolution of 1 km.
    xi = np.asarray(1e-3 * np.abs(x - 1e3 * psmin) - 0.5, dtype=np.int)
    yi = np.asarray(1e-3 * np.abs(y + 1e3 * psmin) - 0.5, dtype=np.int)

    # and we are done!
    return xi, yi


def latlon_to_index(
    lat: np.ndarray, lon: np.ndarray
) -> Tuple[ma.masked_array, ma.masked_array]:
    """
    Convert an array of latitude and longitude (in degrees) into
    a set of BEDMAP data indices.

    Parameters
    ----------
    lat: np.ndarray
        A N-length Numpy array of latitudes (in degrees)
    lon: np.ndarray
        A N-length Numpy array of longitude (in degrees)

    Returns
    -------
    ix, iy: np.ndarray
        The (ix, iy) indices into the BEDMAP2 dataset.
    """
    # get the x,y locations into the grid in meters.
    x, y = latlon_to_xy(lat, lon)

    # and convert these to indices
    return xy_to_index(x, y)


def latlon_to_xy(
    lat: np.ndarray, lon: np.ndarray
) -> Tuple[ma.masked_array, ma.masked_array]:
    """
    Convert an array of latitude and longitude into (x, y) coordinates
    in the South Polar Stereographic Project (in m).

    This uses:
        "Map Projections - A Working Manual" by J.P Snyder"
        https://pubs.usgs.gov/pp/1395/report.pdf
        Stereographic Projections - starting pg. 154. Numerical example on pg. 315
        All page and equation numbers refer to Snyder

    Parameters
    ----------
    lat: np.ndarray
        A N-length Numpy array of latitudes (in degrees)
    lon: np.ndarray
        A N-length Numpy array of longitude (in degrees)

    Returns
    -------
    ps: np.ndarray
        The (x, y) coordinates in the South Pole Stereographic Projection (in m).
    """

    # get references to latitude and longitude in radians
    lat = np.radians(lat)
    lon = np.radians(lon)

    # compute t - Pg. 161 Eq. 15-9
    t = np.tan(np.pi / 4.0 + lat / 2.0) / np.power(
        (1.0 - e * np.sin(-lat)) / (1.0 + e * np.sin(-lat)), e / 2.0
    )

    # this is the true-scale latitude
    latc = -1.239183768915974
    latc = np.radians(-71.0)

    # this is t_c from Pg. 161, Eq., 21-34 in Snyder
    t_c = np.tan(np.pi / 4.0 + latc / 2.0) / np.power(
        (1.0 - e * np.sin(-latc)) / (1.0 + e * np.sin(-latc)), e / 2.0
    )

    # this is m_c from Pg. 161, Eq. 21-34 in Snyder
    # and computed using 14-15 on Pg. 160
    m_c = np.cos(-latc) / np.sqrt(1.0 - e * e * np.power(np.sin(-latc), 2.0))

    # this is a*m_c/t_c - the scale factor multiplied by the coordinate transform
    amtc = a * m_c / t_c

    # we use t, a, t_c, and m_c to compute p.
    p = t * amtc

    # we can then use p to find x, y relative to 0 degrees east.
    # these are in km relative to the center of the Bedmap2 grid.
    x = -p * np.sin(-lon)
    y = p * np.cos(-lon)

    # we mask any coordinates outside the range of bedmap.
    x = ma.masked_outside(x, psmin, psmax)
    y = ma.masked_outside(y, psmin, psmax)

    # stack these into one array and return as meters
    return 1e3 * x, 1e3 * y


def xy_to_latlon(
    x: np.ndarray, y: np.ndarray, lon0: float = 0.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert an array of (x, y) in South Polar Stereographic Projection
    into a set of latitude and longitude (in degrees).

    This uses:
        "Map Projections - A Working Manual" by J.P Snyder"
        https://pubs.usgs.gov/pp/1395/report.pdf
        Stereographic Projections - starting pg. 154. Numerical example on pg. 315
        All page and equation numbers refer to Snyder

    Parameters
    ----------
    x: np.ndarray
        A N-length Numpy array of x-coordinates of South Polar Stereographic
    y: np.ndarray
        A N-length Numpy array of y-coordinates of South Polar Stereographic
    lon0: float
        The longitude at true scale in degrees.

    Returns
    -------
    ll: np.ndarray
        The (lat, lon) coordinates in the degrees.
    """

    # the reference uses -x and -y so inverte these here.
    x = -x
    y = -y

    # this is the true-scale latitude
    latc = np.radians(-71.0)

    # this is t_c from Pg. 161, Eq., 21-34 in Snyder
    t_c = np.tan(np.pi / 4.0 + latc / 2.0) / np.power(
        (1.0 - e * np.sin(-latc)) / (1.0 + e * np.sin(-latc)), e / 2.0
    )

    # this is m_c from Pg. 161, Eq. 21-34 in Snyder
    # and computed using 14-15 on Pg. 160
    m_c = np.cos(-latc) / np.sqrt(1.0 - e * e * np.power(np.sin(-latc), 2.0))

    # compute r/rho
    p = np.sqrt(x * x + y * y)

    # and compute t
    t = p * t_c / (1e3 * a * m_c)

    # there isn't an analytical solution to ps2ll - you can either use
    # an iterative or series solution - we use the series solution
    chi = np.pi / 2.0 - 2 * np.arctan(t)

    # the series solution to the latitude
    lat = chi
    lat += (
        0.5 * (e ** 2)
        + (5.0 / 24.0) * (e ** 4.0)
        + (1.0 / 12.0) * (e ** 6.0)
        + (13.0 / 360.0) * (e ** 8.0)
    ) * np.sin(2 * chi)
    lat += (
        (7.0 / 48.0) * (e ** 4.0)
        + (29.0 / 240.0) * (e ** 6.0)
        + (811.0 / 11520.0) * (e ** 8.0)
    ) * np.sin(4 * chi)
    lat += ((7.0 / 120.0) * (e ** 6.0) + (81.0 / 1120.0) * (e ** 8.0)) * np.sin(6 * chi)
    lat += ((4279.0 / 161280.0) * (e ** 8.0)) * np.sin(8 * chi)

    # and the longitude
    lon = lon0 + np.arctan2(x, -y)

    # correct the signs
    lat = -lat
    lon = -lon

    # and make sure the longitude is in -pi, pi
    lon = np.mod(lon + np.pi, 2 * np.pi) - np.pi

    # stack these into one array and return as meters
    return np.degrees(lat), np.degrees(lon)
