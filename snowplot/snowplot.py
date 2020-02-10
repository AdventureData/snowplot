from .utilities import getLogger

"""Main module."""

def main():

	parser = argparse.ArgumentParser(description='Plot various versions of probe data.')
	parser.add_argument('config_file', help='path to config_file')
	args = parser.parse_args()

	# Provide a opportunity to look at lots
	if args.config_file == None:
		print("Please provide a config file for plots")
		sys.exit()

	# Get the cfg
	ucfg = get_user_config(args.config_file,
						   master_files=['./master.ini','./recipes.ini'],
						   checking_later=False)
	warnings, errors = check_config(ucfg)

	print_config_report(warnings, errors)
	if len(errors) > 0:
		print("Errors in config file. Check report above.")
		sys.exit()

	generate_config(ucfg,'config.ini')
	cfg = ucfg.cfg

	# Cycle through all the files
	for f in cfg['data']['files']:
		bname = os.path.basename(f)
		fname = os.path.expanduser(f)
		fname = os.path.abspath(fname)

		# Open the file and set the index to depth
		df_o = open_adjust_profile(fname, header=cfg['data']['header_size'])

		# Only get the columns were interested in
		df = df_o.copy()

		# Check for smoothing request
		if cfg['profiles']['smoothing'] != None:
			df = df.rolling(window = cfg['profiles']['smoothing']).mean()

		# Check for average profile
		if cfg['profiles']['average']:
			df['average'] = df.mean(axis = 1)
			cfg['profiles']['columns_of_interest'] = ['average']

		fig = plt.figure(figsize=np.array((cfg['output']['figure_size'])))

		#Plot up the data
		for c in cfg['profiles']['columns_of_interest']:
			plt.plot(df[c], df[c].index, label=c)

			# Add the labels for the crystals
			add_plot_labels(df[c], cfg['labeling']['plot_labels'])

			# Fill the plot in like our app
			plt.fill_betweenx(df.index,df[c], 0, interpolate=True)

		if cfg['labeling']['title'] != None:
			plt.title(cfg['labeling']['title'])

		elif cfg['labeling']['use_filename_title']:
			plt.title(os.path.basename(f))

		else:
			raise ValueError("Must either have use title to true or provide a title name")

		#plt.legend()
		plt.xlabel(cfg['labeling']['xlabel'])
		plt.ylabel(cfg['labeling']['ylabel'])

		plt.xlim(cfg['profiles']['xlimits'])

		if cfg['profiles']['ylimits'] != None:
			plt.ylim(cfg['profiles']['ylimits'])

		plt.show()

		#except Exception as e:
		#	print(e)


if __name__ == '__main__':
	main()
