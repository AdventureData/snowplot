from os.path import abspath, basename, expanduser

import numpy as np
import pandas as pd
from snowmicropyn import Profile as SMP
from numpy import poly1d
from .utilities import get_logger

class GenericProfile(object):
    """
    Generic Class for plotting vertical profiles. Is used to standardize a lot
    of data but can be used independently

    Attributes:
        filename:
    """

    def __init__(self, **kwargs):

        # Add config items as attributes
        for k, v in kwargs.items():
            setattr(self, k, v)

        if self.use_filename_title:
            self.title = basename(self.filename)
        else:
            self.title = title.title()

        self.name = type(self).__name__.replace('Profile', '')
        self.log = get_logger(self.name)

        self.filename = abspath(expanduser(self.filename))

        # Number of lines to ignore in a csv
        self.header = 0

        df = self.open()
        process_kw = {}
        for kw in ['smoothing', 'average_columns']:
            if hasattr(self, kw):
                process_kw[kw] = getattr(self, kw)

        self.df = self.processing(df, **process_kw)

        # # Zero base the plot id
        # self.plot_id -= 1

        # Set Tick labels
        self.x_ticks = None

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
            self.log.info('Smoothing with {} point window'.format(self.smoothing))
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
        else:
            self.data_type = 'rad_app'

        names = [ll.lower() for ll in line.split(',')]
        df = pd.read_csv(self.filename, header=self.header, names=names)

        return df

    def additional_processing(self, df):
        """
        Handles when to convert to cm
        """

        if self.data_type == 'rad_app':
            df['depth'] = np.linspace(0, -1.0 * (np.max(df['depth']) / 100.0),
                                      len(df.index))

        # User requested a timeseries plot with an assumed linear depth profile
        if self.assumed_depth is not None:
            self.log.info('Prescribing assumed depth of {self.assumed_depth} cm')
            # if the user assigned a positive depth by accident
            if self.assumed_depth > 0:
                self.assumed_depth *= -1

            # User passed in meters
            if abs(self.assumed_depth) < 2:
                self.assumed_depth *= 100

            self.log.info(f'Prescribing assumed depth of {self.assumed_depth} cm')
            df['depth'] = np.linspace(0, self.assumed_depth, len(df.index))

        # Shift snow surface to 0 cm
        df['depth'] = df['depth'] - self.surface_depth
        if self.bottom_depth is not None:
            df = df.loc[0:self.bottom_depth]

        df.set_index('depth', inplace=True)
        df = df.sort_index()
        if hasattr(self, 'calibration_coefficients'):
            self.log.info(f"Applying calibration to {', '.join(self.columns_to_plot)}")

            poly = poly1d(self.calibration_coefficients)
            df[self.columns_to_plot] = poly(df[self.columns_to_plot])
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
        return df


    def additional_processing(self, df):
        # Convert into CM from MM and set 0 at the start
        self.log.info('Converting `distance` to cm and setting top to 0...')
        df['depth'] = df['distance'].div(-10)
        df = df.set_index('depth')
        df = df.sort_index()
        self.log.info('Converting N into mN...')
        df['force'] = df['force'].mul(1000)  #Put into millinewtons
        return df
class HandHardnessProfile(GenericProfile):
    """
    A class for handling hand hardness data. Currently set for only reading a
    custom file but later will read other data
    """

    def __init__(self, **kwargs):

        text_scale = ['F', '4F', '1F', 'P', 'K', 'I']
        # Build the numeric scale
        self.scale = self._build_scale()

        super(HandHardnessProfile, self).__init__(**kwargs)
        self.fill_solid = True
        self.columns_to_plot = ['numeric']

        # Alternate labels to use for x_tick
        self.x_ticks = text_scale

    def open(self):
        self.log.info("Opening filename {}".format(basename(self.filename)))

        # Simple text file
        if self.filename.split('.')[-1] == 'txt':
            df = self.read_simple_text(self.filename)
            df = df.set_index('depth')
        return df

    def _build_scale(self):
        """
        Returns the mapping of characater data like F+ to a number for plotting
        """
        scale = {}
        count = 1
        for h in ['F', '4F', '1F', 'P', 'K', 'I']:
            hv = h
            if h != 'I':
                for b in ['-', '', '+']:
                    hv = '{}{}'.format(h, b)

                    scale[hv] = count
                    count += 1.0
            else:
                scale[hv] = count
                count += 1.0
        return scale

    def read_snowpilot(filename=None, url=None):
        pass

    def read_simple_text(self, filename):
        """
        Reads in a text file containing only hardness information
        Format is in depth1-depth2:hardness_value
        Args:
            filname: path to the text file
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
