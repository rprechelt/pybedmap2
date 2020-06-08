import numpy as np

import bedmap2
import bedmap2.transform as transform


def test_consistent():
    """
    Generate random (lat, lon) pairs, convert them
    to polar stereographic, and convert them back to
    make sure that the conversions are self consistent.
    """

    # the number of elements we try
    N = 10_000

    # generate lat,lon pairs
    lat = np.random.uniform(-70.0, -90.0, size=N)
    lon = np.random.uniform(-180.0, 180.0, size=N)

    # convert them to x, y in meters.
    x, y = transform.latlon_to_xy(lat, lon)

    # and convert them back to lat lon
    latc, lonc = transform.xy_to_latlon(x, y)

    # and make sure they match
    np.testing.assert_allclose(lat, latc)
    np.testing.assert_allclose(lon, lonc)
