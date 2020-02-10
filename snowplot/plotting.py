import matplotlib.pyplot as plt
import numpy as np
from os.path import basename
from .utilities import get_logger


log = get_logger(__name__)


def add_plot_labels(df, label_list):
	"""
    Adds labels to a plot.

    Args:
        df: pandas dataframe in which the index is the y axis of the plot
        label_list: List of strings containing label and index to place it in the format of (<lable> > <depth>)
	a list of labels in the format of [(<label> > <depth>),]
	"""
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
	# Build plots
	fig = plt.figure(figsize=np.array((cfg['output']['figure_size'])))

	for name, profile in data.items():
	    # Plot up the data
		log.info("Plotting {}".format(name))

		df = profile.df
		print(profile.columns_to_plot)
		for c in profile.columns_to_plot:
			log.debug("\tAdding {}".format(c))
			plt.plot(df[c], df[c].index, label=c)

		# Add the labels for the crystals
		add_plot_labels(df[c], cfg['labeling']['plot_labels'])

		# Fill the plot in like our app
		plt.fill_betweenx(df.index, df[c], 0, interpolate=True)

		if cfg['labeling']['title'] != None:
			plt.title(cfg['labeling']['title'])

		elif cfg['labeling']['use_filename_title']:
			plt.title(basename(profile.filename))

		else:
			raise ValueError("Must either have use title to true or provide a title name")

		#plt.legend()
		plt.xlabel(cfg['labeling']['xlabel'])
		plt.ylabel(cfg['labeling']['ylabel'])

		plt.xlim(cfg['plotting']['xlimits'])

		if cfg['plotting']['ylimits'] != None:
			plt.ylim(cfg['plotting']['ylimits'])

		plt.show()
