import matplotlib.pyplot as plt
import numpy as np
from os.path import join

from .utilities import get_logger
from . import __non_data_sections__

def add_plot_annotations(ax, series, label_list):
    """
Adds labels to a plot.
e.g.  (surface? > -10) places a label at -10 that says surface
Args:
    df: pandas dataframe in which the index is the y axis of the plot
    label_list: a list of labels in the format of [(<label> > <depth>),]
    """
    log = get_logger(__name__)

    if label_list is not None:
        for label in label_list:
            if " " in label:
                l_str = "".join([s for s in label if s not in '()'])
                final_label, depth = l_str.split(">")
                depth = float(depth)
                idx = (np.abs(series.index - depth)).argmin()
                y_val = series.index[idx]
                x_val = series.loc[y_val]
                ax.annotate(final_label, (x_val, y_val), xytext=(x_val * 1.5, y_val * 0.5),
                            arrowprops={'arrowstyle': '->'})


def add_problem_layer(ax, depth):
    """
    Function for adding red lines to a plot. Given a depth, will add a plot

    Args:
            ax: matplotlib subplot axes object to add the line to
            depth: depth in centimeters to add the line at
    """
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
        for name, profile in data.items():
            if nplots > 1:
                ax = axes[profile.plot_id]
            else:
                ax = axes

            # Plot up the data
            df = profile.df

            # Add colums
            c = profile.column_to_plot
            log.debug("Adding {}.{}".format(name, c))
            if profile.is_layered_data:
                plot_data = profile.get_layered_profile()
            else:
                plot_data = df
            plot_data = plot_data.reset_index()
            ax.plot(plot_data[c], plot_data['depth'], c=profile.line_color, label=c)

            # Fill the plot
            if profile.fill_solid:
                log.debug('Applying horizontal fill to {}.{}'
                          ''.format(name, c))

                ax.fill_betweenx(df.index, df[c].astype(float),
                                 np.zeros_like(df[c].shape),
                                 facecolor=profile.fill_color,
                                 interpolate=True)
            # Add_plot_labels
            if profile.plot_labels is not None:
                log.info("Adding {} annotations...".format(len(profile.plot_labels)))
                add_plot_annotations(ax, df[c], profile.plot_labels)

            # Create a problem layer
            if profile.problem_layer is not None:
                depth = profile.problem_layer
                log.info("Adding a problem layer to plot at {}...".format(depth))
                ax.axhline(y=depth, color='r')

            # Custom titles
            if profile.title is not None:
                ax.set_title(profile.title)

            # X axis label
            if profile.xlabel is not None:
                ax.set_xlabel(profile.xlabel.title())

            # Y axis label
            if profile.ylabel is not None:
                ax.set_ylabel(profile.ylabel.title())

            # Set X limits
            if profile.xlimits is not None:
                lims = sorted(profile.ylimits)
                log.debug("Setting x limits to {}:{}".format(*lims))
                ax.set_xlim(*lims)

            # Set y limits
            if profile.ylimits is not None:
                lims = sorted(profile.ylimits)
                log.debug("Setting y limits to {}:{}".format(*lims))
                ax.set_ylim(*lims)

            ax.grid()
            ax.set_axisbelow(True)

    if cfg['output']['filename'] is not None:
        log.info(f"Saving figure to {cfg['output']['filename']}")
        plt.savefig(join(cfg['output']['output_dir'], cfg['output']['filename']))

    if cfg['output']['show_plot']:
        plt.show()
