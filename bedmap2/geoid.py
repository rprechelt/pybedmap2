import numpy as np


def radius(lat: np.ndarray) -> np.ndarray:
    """
    Compute the geocentric radius of the WGS84 ellipsoid in meters.

    Parameters
    ----------
    lat: np.ndarray
        The set of latitudes (in degrees) at which to calculate the radius.

    Returns
    -------
    radius: np.ndarray
        The geocentric radius at each latitude (in meters).
    """

    # equatorial radius of the WGS84 ellipsoid
    a = 6378137

    # flattening of the WGS84 ellipsoid
    f = 1.0 / (298.257223563)

    # the polar radius of the WGS84 ellipsoid
    b = a * (1 - f)

    # we need the cosine and sine of the latitude squared
    sin2 = np.sin(np.radians(lat)) ** 2.0
    cos2 = np.cos(np.radians(lat)) ** 2.0

    # and we need a^2 and b^2
    a2 = a * a
    b2 = b * b

    # compute the squared radius
    r2 = np.asarray(
        (a2 * a2 * cos2 + b2 * b2 * sin2) / (a2 * cos2 + b2 * sin2), dtype=float
    )

    # and use that to compute the geocentric radius
    return np.sqrt(r2)
