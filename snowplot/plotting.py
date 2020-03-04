from os.path import basename

import matplotlib.pyplot as plt
import numpy as np

from .utilities import get_logger


def add_plot_labels(df, label_list):
    """
Adds labels to a plot.

Args:
    df: pandas dataframe in which the index is the y axis of the plot
    label_list: a list of labels in the format of [(<label> > <depth>),]
    """
    log = get_logger(__name__)

    if label_list is not None:
        for l in label_list:
            if " " in l:
                l_str = "".join([s for s in l if s not in '()'])
                label, depth = l_str.split(">")
                depth = float(depth)
                idx = (np.abs(df.index - depth)).argmin()
                y_val = df.index[idx]
                x_val = df.loc[y_val] + 150
                plt.annotate(label, (x_val, y_val))


def add_problem_layer(ax, depth):
    '''
    Function for adding red lines to a plot. Given a depth, will add a plot

    Args:
            ax: matplotlib subplot axes object to add the line to
            depth: depth in centimeters to add the line at
    Returns:
            ax: axes plot object with the red line added
    '''
    ax.plot([0, 10], [depth, depth], 'r')
    # return ax


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
    nplots = cfg['plotting']['num_subplots']
    fsize[0] = fsize[0] * nplots

    # Build (sub)plots
    fig, axes = plt.subplots(1, nplots, figsize=fsize)

    log.info("Generating {} subplots...".format(nplots))
    for i in range(nplots):
        if nplots > 1:
            ax = axes[i]
        else:
            ax = axes

        pid = i + 1

        for name, profile in data.items():
            if profile.plot_id == i:
                # Plot up the data
                log.info("Adding {} to plot #{}".format(name, pid))
                df = profile.df

                # Add colums

                for c in profile.columns_to_plot:
                    log.debug("Adding {}.{}".format(name, c))
                    ax.plot(df[c], df[c].index, c=profile.color, label=c)

                    # Fill the plot
                    if profile.fill_solid:
                        log.debug('Applying horizontal fill to {}.{}'
                                  ''.format(name, c))
                        ax.fill_betweenx(df.index, np.array(df[c], dtype=float),
                                         np.zeros_like(df[c].shape),
                                         facecolor=profile.color,
                                         interpolate=True)

        if cfg['labeling']['problem_layer'] is not None:
            depth = float(cfg['labeling']['problem_layer'][i])
            log.info("Adding a problem layer to plot at {}...".format(depth))
            ax.plot([0, 10000], [depth, depth], 'r')

        # Custom titles
        if cfg['labeling']['title'] is not None:
            title = cfg['labeling']['title'][i].title()
            ax.set_title(title)

        # add_plot_labels
        if cfg['labeling']['xlabel'] is not None:
            ax.set_xlabel(cfg['labeling']['xlabel'][i].title())

        ax.set_ylabel(cfg['labeling']['ylabel'].title())

        # Set limits
        ax.set_xlim(cfg['plotting']['xlimits'][2 * i:2 * i + 2])

        if cfg['plotting']['ylimits'] is not None:
            ax.set_ylim(cfg['plotting']['ylimits'])

        ax.grid()
        ax.set_axisbelow(True)
    plt.show()
