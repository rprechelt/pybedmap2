import os.path as op

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

import bedmap2

FIGDIR = op.join(op.dirname(__file__), "figures")


def test_surface_plot():
    """
    Make a plot of the surface height of the continent.
    """

    # create the figure
    fig, ax = plt.subplots()

    # load the dataset
    surface = bedmap2.load_data("surface")

    # show the plot
    im = ax.imshow(surface, cmap="inferno", extent=[-3333.5, 3333.5, -3333.5, 3333.5])

    # create the colorbar axis
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)

    # and some labels
    ax.set(xlabel="X [km]", ylabel="Y [km]", title="Surface Height")

    # and add the colorbar
    cbar = plt.colorbar(im, cax=cax)
    cbar.set_label("[m]")

    # and show the plot
    fig.savefig(f"{FIGDIR}/surface.png")
