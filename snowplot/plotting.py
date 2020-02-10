from matplotlib.pyplot import  plt
from .utilities import getLogger


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
			plt.annotate(label,( x_val,y_val))
