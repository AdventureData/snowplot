from .utilities import getLogger

class LyteProbe(object):
    """
    Class used for managing a profile taking with the Lyte probe from
    Adventure Data.

    The class is prepared to manage either a profile taken from the mobile app
    or through the commandline using radicl.

    """
    def __init__(self, fname):

        # First attempt the app
        try:
            df = open_adjust_profile(fname, header=11, depth_to_cm=True)
        # Assum radicl
        except:
            df = open_adjust_profile(fname, header=5, depth_to_cm=False)
        finally:

    def open_adjust_profile(self, fname, header=11, depth_to_cm=True):

    	df = pd.read_csv(fname, header=header)

    	# Convert to cm
    	if depth_to_cm:
    		df['DEPTH'] = np.linspace(0,-1.0 * (np.max(df['DEPTH']) / 100.0), len(df.index))

    	df.set_index('DEPTH', inplace=True)

    	return df
