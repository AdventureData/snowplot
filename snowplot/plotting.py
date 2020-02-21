import matplotlib.pyplot as plt
import numpy as np
from os.path import basename
from .utilities import get_logger



def add_plot_labels(df, label_list):
	"""
    Adds labels to a plot.

    Args:
        df: pandas dataframe in which the index is the y axis of the plot
        label_list: a list of labels in the format of [(<label> > <depth>),]
	"""
	log = get_logger(__name__)

	if label_list != None:
		for l in label_list:
			if " " in l:
				l_str = "".join([s for s in l if s not in '()'])
				label, depth  = l_str.split(">")
				depth = float(depth)
				idx = (np.abs(df.index - depth)).argmin()
				y_val = df.index[idx]
				x_val = df.loc[y_val] + 150
				plt.annotate(label,( x_val, y_val))

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
	nplots =  cfg['plotting']['num_subplots']
	fsize[0] = fsize[0] * nplots

	# Build (sub)plots
	fig, axes = plt.subplots(1, nplots, figsize=fsize)

	for name, profile in data.items():
	    # Plot up the data
		log.info("Plotting {}".format(name))

		df = profile.df
		pid = profile.plot_id
		ax = axes[pid]

		for c in profile.columns_to_plot:
			log.debug("Adding {}.{}".format(name, c))
			ax.plot(df[c], df[c].index, c=profile.color, label=c)

			# Fill the plot
			if profile.fill_solid:
				ax.fill_betweenx(df.index, np.array(df[c],dtype=int), np.zeros_like(df[c].shape), facecolor=profile.color, interpolate=True)

		# Custom titles
		if cfg['labeling']['title'] != None:
			title = cfg['labeling']['title'][pid].title()
			ax.set_title(title)

		# add_plot_labels
		ax.set_xlabel(cfg['labeling']['xlabel'][pid].title())
		ax.set_ylabel(cfg['labeling']['ylabel'].title())

		# Set limits
		print(cfg['plotting']['xlimits'][2*pid:pid+2])
		ax.set_xlim(cfg['plotting']['xlimits'][2*pid:2*pid+2])

		if cfg['plotting']['ylimits'] != None:
			ax.set_ylim(cfg['plotting']['ylimits'])

	plt.show()
