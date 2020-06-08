from typing import Tuple

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import bedmap2.data as data
import bedmap2.geoid as geoid
import bedmap2.transform as transform


def xy_along_path(
    latstart: float,
    lonstart: float,
    latend: float,
    lonend: float,
    stepsize: float = 0.5,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute a path in (x, y) between (latstart, lonstart) and
    (latend, lonend) with `stepsize` (in km).

    Parameters
    ----------
    latstart: float
        The latitude of the starting point (in degrees).
    lonstart: float
        The longitude of the starting point (in degrees).
    latend: float
        The latitude of the end point (in degrees).
    lonend: float
        The longitude of the end point (in degrees).
    stepsize: float
        The step-size between points (in km).

    Returns
    -------
    x, y: Tuple[np.ndarray, np.ndarray]
        The (x, y) arrays of this path.
    """
    # get the x and y-location of the start and end locations
    xstart, ystart = transform.latlon_to_xy(latstart, lonstart)
    xend, yend = transform.latlon_to_xy(latend, lonend)

    # if xstart and xend are the same, just sample in y.
    if np.allclose(xstart, xend):

        # check the sign of yend -> ystart
        sgn = np.sign(yend - ystart)

        # create y, and then x which is all zeros
        y = np.arange(ystart, yend, sgn * stepsize)
        x = np.zeros_like(y)

        # and we are done
        return x, y
    else:

        # check the sign of xstart - xend - this determines which step direction
        sgn = np.sign(xend - xstart)

        # sample the x-coordinates finer than 1 km resolution
        x = np.arange(xstart, xend, sgn * stepsize)

        # and generate the appropiate y-coordinates on the linee
        y = (x - xstart) * ((ystart - yend) / (xend - xstart)) + ystart

        # and we are done
        return x, y


def flat_profile(
    latstart: float, lonstart: float, latend: float, lonend: float
) -> matplotlib.figure.Figure:
    """
    Produce a figure containing the BEDMAP2 profile between
    (latstart, lonstart) and (latend, lonend).

    This is done assuming a flattened Earth profile.

    Parameters
    ----------
    latstart: float
        The starting latitude (in degrees).
    lonstart: float
        The starting longitude (in degrees).
    latend: float
        The end latitude (in degrees).
    lonend: float
        The end longitude (in degrees).

    Returns
    -------
    figure: matplotlib.figure.Figure
        The matplotlib figure.
    """

    # get the series of x, y points in meters along the path
    x, y = xy_along_path(latstart, lonstart, latend, lonend)

    # get the surface height
    surface = data.surface(x, y, mode="xy") / 1000.0

    # and the bed height
    bed = data.bed(x, y, mode="xy") / 1000.0

    # and the thickness of the ice
    thickness = data.thickness(x, y, mode="xy") / 1000.0

    # create the figure and plot
    fig, ax = plt.subplots()

    # compute the range along this trajectory [in km]
    drange = np.sqrt((x - x[0]) ** 2.0 + (y - y[0]) ** 2.0) / 1e3

    # compute the minimum value of the plot
    minh = np.min(bed)

    # fill in the ocean - this generally shouldn't be seen.
    ax.fill_between(drange, 0.0, y2=minh, color="dodgerblue")

    # fill any subsurface water pockets
    ax.fill_between(drange, surface - thickness, y2=minh, color="dodgerblue")

    # plot the surface height
    ax.fill_between(drange, surface, y2=surface - thickness, color="skyblue")

    # and plot the bed level
    ax.fill_between(drange, bed, y2=minh, color="sienna")

    # add some labels
    ax.set(xlabel="Range [km]", ylabel="Height [km]")

    # set some appropriate axis limits
    ax.set_xlim([0, drange[-1]])
    ax.set_ylim(bottom=minh)

    # and return the figure
    return fig


def curved_profile(
    latstart: float, lonstart: float, latend: float, lonend: float, curved: bool = False
) -> matplotlib.figure.Figure:
    """
    Produce a figure containing the BEDMAP2 profile between
    (latstart, lonstart) and (latend, lonend).

    This is done assuming assuming a curved Earth profile.

    Parameters
    ----------
    latstart: float
        The starting latitude (in degrees).
    lonstart: float
        The starting longitude (in degrees).
    latend: float
        The end latitude (in degrees).
    lonend: float
        The end longitude (in degrees).

    Returns
    -------
    figure: matplotlib.figure.Figure
        The matplotlib figure.
    """

    # get the series of x, y points in meters along the path
    x, y = xy_along_path(latstart, lonstart, latend, lonend)

    # the number of points is the size of x
    npoints = x.size

    # get the latitudes associated with each step in the path
    lat, _ = transform.xy_to_latlon(x, y)

    # and get the radius associated with each of these points
    radius = geoid.radius(lat) / 1000.0

    # compute the range along this trajectory [in km]
    drange = np.sqrt((x - x[0]) ** 2.0 + (y - y[0]) ** 2.0) / 1e3

    # compute the theta angle associated with each point
    theta = drange / radius

    # make theta symmetric about the middle of our plot
    theta -= theta[npoints // 2]

    # get the surface height
    surface = data.surface(x, y, mode="xy") / 1000.0 + radius

    # and the bed height
    bed = data.bed(x, y, mode="xy") / 1000.0 + radius

    # and the thickness of the ice
    thickness = data.thickness(x, y, mode="xy") / 1000.0

    # create the figure and plot
    fig, ax = plt.subplots()

    # compute the minimum value of the plot
    minh = np.min(np.cos(theta[npoints // 2]) * bed)
    maxh = np.max(np.cos(theta[npoints // 2]) * surface) + 0.3

    # fill in the ocean - this generally shouldn't be seen.
    ax.fill_between(
        np.sin(theta) * radius, np.cos(theta) * radius, y2=0, color="dodgerblue"
    )

    # plot the surface height
    ax.fill_between(
        np.sin(theta) * surface,
        np.cos(theta) * surface,
        y2=np.cos(theta) * (surface - thickness),
        color="skyblue",
    )

    # fill any subsurface water pockets
    ax.fill_between(
        np.sin(theta) * (surface - thickness),
        np.cos(theta) * (surface - thickness),
        y2=minh,
        color="dodgerblue",
    )

    # and also fill in the bed level
    ax.fill_between(np.sin(theta) * bed, np.cos(theta) * bed, y2=0.0, color="sienna")

    # and finally plot the sea-level radius
    ax.plot(np.sin(theta) * radius, np.cos(theta) * radius, linestyle=":", color="k")

    # add some labels
    ax.set(xlabel="Linear Range [km]", ylabel="Geocentric Radius [km]")

    # set some appropriate axis limits
    ax.set_xlim([np.sin(theta[0]) * radius[0], np.sin(theta[-1]) * radius[-1]])
    ax.set_ylim(bottom=minh, top=maxh)

    # and return the figure
    return fig
