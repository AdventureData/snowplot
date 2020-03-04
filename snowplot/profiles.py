from os.path import abspath, basename, expanduser

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from snowmicropyn import Profile as SMP

from .utilities import get_logger


class GenericProfile(object):
    """
    Generic Class for plotting vertical profiles. Is used to stadnardize a lot
    of data but can be used independently
    """

    def __init__(self, **kwargs):

        # Add config items as attributes
        for k, v in kwargs.items():
            setattr(self, k, v)

        name = type(self).__name__.replace('Profile', '')
        self.log = get_logger(name)

        self.filename = abspath(expanduser(self.filename))

        # Number of lines to ignore in a csv
        self.header = 0

        df = self.open()
        self.df = self.processing(df)

        # Zero base the plot id
        self.plot_id -= 1

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
        if smoothing is not None:
            self.log.info('Smoothing with {}'.format(self.smoothing))
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
                    k, v = line.split('=')
                    k, v = (c.lower().strip() for c in [k, v])
                    self.header_info[k] = v
                else:
                    self.header = i
                    self.log.debug(
                        "Header length found to be {} lines".format(i))
                    break

            fp.close()

        if 'radicl version' in self.header_info.keys():
            self.data_type = 'radicl'
            columns = ['depth', 'sensor_1', 'sensor_2', 'sensor_3', 'sensor_4']

        else:
            self.data_type = 'rad_app'
            columns = [
                'sample',
                'depth',
                'sensor_1',
                'sensor_2',
                'sensor_3',
                'sensor_4']

        df = pd.read_csv(self.filename, header=self.header, names=columns)

        return df

    def additional_processing(self, df):
        """
        Handles when to convert to cm
        """
        if self.data_type == 'rad_app':
            df['depth'] = np.linspace(0, -1.0 * (np.max(df['depth']) / 100.0),
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

    def open(self):
        self.log.info("Opening filename {}".format(basename(self.filename)))
        p = SMP.load(self.filename)
        ts = p.timestamp
        coords = p.coordinates
        df = p.samples

        df['depth'] = df['distance'].div(-10)
        df = df.set_index('depth')
        return df


class HandHardnessProfile(GenericProfile):
    """
    A class for handling hand hardness data. Currently set for only reading a
    custom file but later will read other data
    """

    def __init__(self, **kwargs):

        # Build the numeric scale
        scale = {}
        count = 1
        for h in ['F', '4F', '1F', 'P', 'K', 'I']:
            scale[h] = count
            count += 1.0

            if h != 'I':
                for b in ['-', '+']:
                    scale['{}{}'.format(h, b)] = count
                    count += 1.0
        print(count)
        self.scale = scale

        super(HandHardnessProfile, self).__init__(**kwargs)
        self.fill_solid = True
        self.columns_to_plot = ['numeric']

    def open(self):
        self.log.info("Opening filename {}".format(basename(self.filename)))

        # Simple text file
        if self.filename.split('.')[-1] == 'txt':
            df = self.read_simple_text(self.filename)
            df = df.set_index('depth')
            print(df)
        return df

    def read_snowpilot(filename=None, url=None):
        pass

    def read_simple_text(self, filename):
        """
        Reads in a text file containing only hardness information
        Format is in depth1-depth2:hardness_value
        Args:
            filname: path to the text file
        Returns:
            df: pandas dataframe
        """
        depth = []
        hardness = []

        # open text file
        with open(filename, 'r') as fp:
            lines = fp.readlines()
            fp.close()

        for i, line in enumerate(lines):

            # Parse a line entry
            if '=' in line:
                data = line.split('=')

                if len(data) == 2:
                    depth_range = data[0]
                    hardness_range = data[1]

                else:
                    raise ValueError("Only one = can be used to represent "
                                     "hand hardness in text file. "
                                     "On line #{}.".format(i))
                # parse depth range
                if '-' in depth_range:
                    d = depth_range.split('-')
                    for dv in d:
                        depth.append(float(dv.strip()))

                # parse hardness scale when a range
                if ',' in hardness_range:
                    hv = hardness_range.split(',')

                # Single hardness value but represents two spots
                else:
                    hv = [hardness_range, hardness_range]

                # Parse the values and map them
                for h in hv:
                    hardness.append(h.upper().strip())

        df = pd.DataFrame(columns=['depth', 'hardness', 'numeric'])

        # Check for positive depth
        mn = min(depth)
        mx = max(depth)
        if mx > 0 and mn >= 0:
            self.log.debug('Positive snow height, inverting to negative')
            depth = [d - mx for d in depth]

        # Cap the data so it looks clean
        data = {'depth': 0, 'hardness': '-', 'numeric': 0}
        df = df.append(data, ignore_index=True)

        for d, h in zip(depth, hardness):
            data = {'depth': d, 'hardness': h, 'numeric': self.scale[h]}
            df = df.append(data, ignore_index=True)

        # Cap the data so it looks good
        data = {'depth': min(depth), 'hardness': '-', 'numeric': 0}
        df = df.append(data, ignore_index=True)

        return df
