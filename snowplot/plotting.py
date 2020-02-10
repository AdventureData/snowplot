import matplotlib.pyplot as plt
import numpy as np
from os.path import basename
from .utilities import get_logger



def add_plot_labels(df, label_list):
	"""
    Adds labels to a plot.

    Args:
        df: pandas dataframe in which the index is the y axis of the plot
        label_list: List of strings containing label and index to place it in the format of (<lable> > <depth>)
	a list of labels in the format of [(<label> > <depth>),]
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
	# Build plots
	fig = plt.figure(figsize=np.array((cfg['output']['figure_size'])))
	log = get_logger(__name__)

	for name, profile in data.items():
	    # Plot up the data
		log.info("Plotting {}".format(name))

		df = profile.df
		for c in profile.columns_to_plot:
			log.debug("Adding {}.{}".format(name, c))
			plt.plot(df[c], df[c].index, c=profile.color, label=c)

		# Fill the plot in like our app
		if profile.fill_solid:
			plt.fill_betweenx(df.index, df[c], 0, facecolor=profile.color, interpolate=True)

	# Custom title
	if cfg['labeling']['title'] != None:
		title = cfg['labeling']['title'].title()

	# Use the file name
	elif cfg['labeling']['use_filename_title']:
		title = []
		for name, profile in data.items():
			title.append(basename(profile.filename))
		title = ' vs '.join(title)

	else:
		raise ValueError("Must either have use title to true or provide a title name")

	# Title
	plt.title(title)

	# add_plot_labels
	plt.xlabel(cfg['labeling']['xlabel'].title())
	plt.ylabel(cfg['labeling']['ylabel'].title())

	plt.xlim(cfg['plotting']['xlimits'])

	if cfg['plotting']['ylimits'] != None:
		plt.ylim(cfg['plotting']['ylimits'])

	plt.show()
