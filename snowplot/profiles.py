from .utilities import get_logger
import numpy as np
import pandas as pd
from snowmicropyn import Profile as SMP
from os.path import abspath, expanduser, basename

class GenericProfile(object):
    """
    Generic Class for plotting vertical profiles. Is used to stadnardize a lot
    of data but can be used independently
    """

    def __init__(self, **kwargs):

        # Add config items as attributes
        for k,v in kwargs.items():
            setattr(self, k, v)

        name = type(self).__name__.replace('Profile','')
        self.log = get_logger(name)

        self.filename = abspath(expanduser(self.filename))

        # Number of lines to ignore in a csv
        self.header = 0

        df = self.open()
        self.df = self.processing(df)

    def open(self):
        """
        Function used to standardize opening data sets, Should be overwritten if
        data doesn't fit into the csv format

        Returns:
            df: Pandas dataframe indexed by the vertical axis (usually depth)
        """
        pass

    def processing(self, df, smoothing=None, average_columns=False):
        """
        Processing to apply to the dataframe to make it more visually appealing
        Also has a end point for users to define their own processing function

        Args:
            df: Pandas dataframe with an index set as the y axis of the plot
            smoothing: Integer representing the size of the moving window to
                       average over
            average_columns: Create an average column representing the average
                             of all the columns
        Returns:
            df: Pandas dataframe
        """

        # Smooth profiles vertically
        if smoothing != None:
            df = df.rolling(window=smoothing).mean()

        # Check for average profile
        if average_columns:
            df['average'] = df.mean(axis=1)

        # Apply user defined additional_processing
        df = self.additional_processing(df)

        return df

    def additional_processing(self, df):
        """
        Abstract Processing function to redefine for individual datatypes. Automatically
        called in processing.

        Args:
            df: dataframe
        Returns:
            df: pandas dataframe
        """
        return df

class LyteProbeProfile(GenericProfile):
    """
    Class used for managing a profile taking with the Lyte probe from
    Adventure Data.

    The class is prepared to manage either a profile taken from the mobile app
    or through the commandline using radicl.

    """

    def __init__(self, **kwargs):
        super(LyteProbeProfile, self).__init__(**kwargs)

    def open(self):
        """
        Lyte probe specific profile opening function attempts to open it as if
        it was from the app, if it fails tries again assuming it is from
        radicl
        """
        self.log.info("Opening filename {}".format(basename(self.filename)))

        # Collect the header
        self.header_info = {}

        with open(self.filename) as fp:
            for i, line in enumerate(fp):
                if '=' in line:
                    k,v = line.split('=')
                    k,v = (c.lower().strip() for c in [k,v])
                    self.header_info[k] = v
                else:
                    self.header = i
                    self.log.debug("Header length found to be {} lines".format(i))
                    break

            fp.close()

        if 'radicl version' in  self.header_info.keys():
            self.data_type = 'radicl'
            columns = ['depth','sensor_1','sensor_2','sensor_3','sensor_4']

        else:
            self.data_type = 'rad_app'
            columns = ['sample','depth','sensor_1','sensor_2','sensor_3','sensor_4']

        df = pd.read_csv(self.filename, header=self.header, names=columns)

        return df

    def additional_processing(self, df):
        """
        Handles when to convert to cm
        """
        if self.data_type == 'rad_app':
        	df['depth'] = np.linspace(0,-1.0 * (np.max(df['depth']) / 100.0),
                                         len(df.index))

        df.set_index('depth', inplace=True)
        return df


class SnowMicroPenProfile(GenericProfile):
    """
    A simple class reflection of the python package snowmicropyn class for
    smp measurements
    """
    def __init__(self, **kwargs):
        super(SnowMicroPenProfile, self).__init__(**kwargs)
        self.columns_to_plot = ['force']
        print(self.color)

    def open(self):
        self.log.info("Opening filename {}".format(basename(self.filename)))
        p = SMP.load(self.filename)
        ts = p.timestamp
        coords = p.coordinates
        df = p.samples

        df['depth'] = df['distance'].div(-10)
        df = df.set_index('depth')
        return df
