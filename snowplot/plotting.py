from os.path import basename

import matplotlib.pyplot as plt
import numpy as np

from .utilities import get_logger
from . import __non_data_sections__

def add_plot_labels(ax, df, plot_labels):
    """
    Adds labels to a plot.

    Args:
        df: pandas dataframe in which the index is the y axis of the plot
        plot_labels: a list of labels in the format of [(<label> > <depth>),]
    """
    for l in plot_labels:
        if " " in l:
            l_str = "".join([s for s in l if s not in '()'])
            label, depth = l_str.split(">")
            depth = float(depth)
            idx = (np.abs(df.index - depth)).argmin()
            y_val = df.index[idx]
            x_val = df.loc[y_val] + 150
            ax.annotate(label, (x_val, y_val))

def add_problem_layer(ax, depth):
    '''
    Function for adding red lines to a plot. Given a depth, will add a plot

    Args:
            ax: matplotlib subplot axes object to add the line to
            depth: depth in centimeters to add the line at
    '''
    ax.axhline(y=depth, color='r')


def build_figure(data, cfg):
    """
    Builds the final figure using the config and a dictionary of data profiles

    Args:
            data: Dictionary of data.profiles object to be plotted
            cfg: dictionary of config options containing at least one profile,
                    output, and labeling sections

    """
    log = get_logger(__name__)

    # the size of a single plot
    fsize = np.array(cfg['output']['figure_size'])

    # Expands the size in the x dir for each plot
    plot_sections = [s for s in cfg.keys() if s not in __non_data_sections__]
    nplots = len(plot_sections)
    fsize[0] = fsize[0] * nplots

    # Build (sub)plots
    fig, axes = plt.subplots(1, nplots, figsize=fsize)

    log.info("Generating {} subplots...".format(nplots))
    for i in range(nplots):
        if nplots > 1:
            ax = axes[i]
        else:
            ax = axes

        for name, profile in data.items():
            # Plot up the data
            #log.info("Adding {} to plot #{}".format(name, pid))
            df = profile.df

            # Add colums
            for c in profile.columns_to_plot:
                log.debug("Adding {}.{}".format(name, c))
                ax.plot(df[c], df[c].index, c=profile.color, label=c)

                # Fill the plot
                if profile.fill_solid:
                    log.debug('Applying horizontal fill to {}.{}'
                              ''.format(name, c))
                    ax.fill_betweenx(df.index, np.array(df[c].values, dtype=np.float),
                                     np.zeros_like(df[c].shape),
                                     facecolor=profile.color,
                                     interpolate=True)
                # Add_plot_labels
                if profile. plot_labels != None:
                    log.info("Adding {} annotations...".format(len(profile.plot_labels)))
                    add_plot_labels(ax, df[c],  profile.plot_labels)

                # Create a problem layer
                if profile.problem_layer is not None:
                    depth = profile.problem_layer
                    log.info("Adding a problem layer to plot at {}...".format(depth))
                    ax.axhline(y=depth, color='r')

                # Custom titles
                if profile.title is not None:
                    title = profile.title.title()
                    ax.set_title(title)

                # X axis label
                if profile.xlabel is not None:
                    ax.set_xlabel(profile.xlabel.title())

                # Y axis label
                if profile.ylabel is not None:
                    ax.set_xlabel(profile.ylabel.title())

                # Set X limits
                if profile.xlimits is not None:
                    log.debug("Setting x limits to {}:{}".format(*profile.xlimits))
                    ax.set_xlim(*profile.xlimits)

                # Set y limits
                if profile.ylimits is not None:
                    log.debug("Setting y limits to {}:{}".format(*profile.ylimits))
                    ax.set_ylim(*profile.ylimits)

                ax.grid()
                ax.set_axisbelow(True)

    if cfg['output']['show_plot']:
        plt.show()
