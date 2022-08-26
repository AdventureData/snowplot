from os.path import abspath, basename, expanduser

import numpy as np
import pandas as pd
from PIL import Image
from numpy import poly1d
from snowmicropyn import Profile as SMP
from study_lyte.depth import get_depth_from_acceleration
from study_lyte.detect import get_acceleration_stop, get_nir_surface, get_acceleration_start
from study_lyte.io import read_csv

from .utilities import get_logger, titlize


class GenericProfile(object):
    """
    Generic Class for plotting vertical profiles. Is used to standardize a lot
    of data but can be used independently

    Attributes:
        filename:
    """

    def __init__(self, **kwargs):

        # Set Tick labels
        self.x_ticks = None
        self.column_to_plot = None
        self._scale = None

        # Use for density profiles, hand hardness profiles any data with distinguished layers
        self.is_layered_data = False

        # Add config items as attributes
        for k, v in kwargs.items():
            setattr(self, k, v)

        if self.use_filename_title:
            self.title = basename(self.filename)

        elif self.title is not None:
            self.title = titlize(self.title)

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
            self.log.info('Smoothing with a {} point window'.format(self.smoothing))
            df = df.rolling(window=smoothing).mean()

        # Check for average profile
        if average_columns:
            df['average'] = df.mean(axis=1)

        # Apply user defined additional_processing
        df = self.additional_processing(df)

        if self.xlimits is None and self.column_to_plot is not None:
            self.xlimits = [df[self.column_to_plot].min(), df[self.column_to_plot].max()]

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
        df, self.header_info = read_csv(self.filename)

        # Config lower cases everything so letsd find a matching name
        columns = list(df.columns)
        idx = [c.lower() for c in columns].index(self.column_to_plot.lower())
        self.column_to_plot = columns[idx]
        df[self.column_to_plot] = df[self.column_to_plot].astype(float)

        if 'radicl VERSION' in self.header_info.keys():
            self.data_type = 'radicl'
        else:
            self.data_type = 'rad_app'

        return df

    def additional_processing(self, df):
        """
        Handles when to convert to cm
        """
        if self.data_type == 'rad_app':
            df['depth'] = np.linspace(0, -1.0 * (np.max(df['depth']) / 100.0),
                                      len(df.index))

        if self.data_type == 'radicl':
            if 'acceleration' in df.columns:
                acol = 'acceleration'
            else:
                acol = 'Y-Axis'
            if 'time' not in df.columns:
                df['time'] = np.linspace(0, len(df.index) * 16000, len(df.index))
            # Detect our events
            n_basis = int(0.01 * len(df.index))

            start = get_acceleration_start(df[acol].values, n_points_for_basis=n_basis, threshold=0.1)
            stop = get_acceleration_stop(df[acol].values, n_points_for_basis=n_basis, threshold=0.7)
            surface = get_nir_surface(df['Sensor2'].iloc[start:stop], df['Sensor3'].iloc[start:stop], threshold=0.02)
            surface = surface + start

            if self.depth_method in ['acc', 'avg']:
                self.log.info('Calculating Depth from accelerometer...')
                acc_depth = get_depth_from_acceleration(df)
                acc_depth['time'] = df.index
                acc_depth.set_index('time', inplace=True)

                df['acc_depth'] = acc_depth[acol].mul(-100)
                if self.depth_method == 'acc':
                    df['depth'] = df['acc_depth'].copy()

                elif self.depth_method == 'avg':
                    df['acc_depth'] = df[['depth', 'acc_depth']].mean(axis=0)

            if self.column_to_plot == 'sensor1':
                df['depth'] = df['depth'] - 4.5
            surface_depth = df['depth'].iloc[surface]
            if self.autocrop:
                bottom_depth = df['depth'].iloc[stop]
                df = df.iloc[surface:stop]
                self.log.info(f'Using autocropping methods, cropping data to {surface_depth:0.0f} cm to '
                              f'{bottom_depth:0.0f} cm (HS = {surface_depth - bottom_depth:0.0f} cm)')

        # User requested a timeseries plot with an assumed linear depth profile
        elif self.assumed_depth is not None:
            # if the user assigned a positive depth by accident
            if self.assumed_depth > 0:
                self.assumed_depth *= -1

            # User passed in meters
            if abs(self.assumed_depth) < 2:
                self.assumed_depth *= 100

            self.log.info(f'Prescribing assumed depth of {self.assumed_depth} cm')
            df['depth'] = np.linspace(0, self.assumed_depth, len(df.index))

        # Shift snow surface to 0 cm
        if self.surface_depth is not None:
            if self.column_to_plot == 'Sensor1':
                df['depth'] = df['depth'] - 4.5

            df['depth'] = df['depth'] - self.surface_depth

        df.set_index('depth', inplace=True)
        df = df.sort_index()

        if self.bottom_depth is not None:
            df = df.loc[0:self.bottom_depth]

        if hasattr(self, 'calibration_coefficients'):
            if self.calibration_coefficients is not None:
                self.log.info(f"Applying calibration to {self.column_to_plot}")

                poly = poly1d(self.calibration_coefficients)
                df[self.column_to_plot] = poly(df[self.column_to_plot])
        return df


class SnowMicroPenProfile(GenericProfile):
    """
    A simple class reflection of the python package snowmicropyn class for
    smp measurements
    """

    def __init__(self, **kwargs):
        super(SnowMicroPenProfile, self).__init__(**kwargs)
        self.column_to_plot = 'force'

    def open(self):
        self.log.info("Opening filename {}".format(basename(self.filename)))
        p = SMP.load(self.filename)
        ts = p.timestamp
        t_str = ts.strftime('%H:%M:%S')
        self.log.info(f"Profile was recorded at {t_str} {ts.tzinfo}")
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
        df['force'] = df['force'].mul(1000)  # Put into millinewtons
        return df


class LayeredProfile(GenericProfile):
    _text_scale = []  # Define for each class
    _snowex_column = None

    def __init__(self, **kwargs):
        super(LayeredProfile, self).__init__(**kwargs)
        self.is_layered_data = True
        self.fill_solid = True
        self.column_to_plot = 'numeric'
        self._scale = None
        # Alternate labels to use for x_tick
        self.x_ticks = self._text_scale # TODO this needs adjusting for hand hardness

        # if self.xlimits is not None:
        #     for i, v in enumerate(self.xlimits):
        #         if type(v) is str:
        #             self.xlimits[i] = self.scale[v]
        # print("")
    def open(self):
        self.log.info("Opening filename {}".format(basename(self.filename)))

        ext = self.filename.split('.')[-1]
        # Simple text file
        if ext == 'txt':
            df = self.read_simple_text(self.filename)
            df = df.set_index('depth')

        # Try snowex reader
        elif ext == 'csv':
            df = self.read_snowex_csv(self.filename)
        else:
            raise NotImplemented('Hand hardness profiles that are not simple text files have not been implemented yet')

        return df

    @property
    def scale(self):
        """
        Returns the mapping of characater data like F+ to a number for plotting
        """
        if self._scale is None:
            self._scale = {}
            for i, h in enumerate(self._text_scale):
                self._scale[h] = i + 1
        return self._scale

    def get_layered_profile(self):
        """
        Returns a profile with added zeros in the x to create the appearance of
        outlined layers

        Returns:
        """
        temp = self.df.reset_index()
        final = pd.DataFrame()
        depth = []
        data = []
        layers = []
        index = []
        d = {}
        for i, layer in enumerate(temp['layer_number'].unique()):
            layer_data = temp[temp['layer_number'] == layer]
            # Create the top zero layer
            index.append(i * 4)
            depth.append(layer_data['depth'].max())
            data.append(0)
            layers.append(layer)

            # Add the data
            values = list(layer_data[self.column_to_plot].values)
            n = len(values)
            index += [idx + (i * 4 + 1) for idx in range(n)]
            depth += list(layer_data['depth'].values)
            data += values
            layers += [layer] * n

            # Add a final zero layer
            index.append(index[-1] + 1)
            depth.append(layer_data['depth'].min())
            data.append(0)
            layers.append(layer)

        # Wrap it up
        d['index'] = index
        d[self.column_to_plot] = data
        d['depth'] = depth
        d['layer_number'] = layers
        final = pd.DataFrame.from_dict(d).set_index('index')
        return final

    def read_simple_text(self, filename):
        pass

    def read_snowex_csv(self, filename):
        """
        Read in a csv from snowex campaign
        Args:
            filename: Path to a csv containing stratigraphy data
        Returns:
            df: pandas dataframe
        """
        with open(filename, 'r') as fp:
            for i, line in enumerate(fp):
                if line[0] != '#':
                    break

        df = pd.read_csv(filename, header=i - 1)

        # Add in the important information for plotting
        df['layer_number'] = range(0, len(df.index))
        df['numeric'] = df.apply(lambda row: self.scale[row[self._snowex_column]], axis=1)

        # Copy the info for top and botom depths and then merge back together
        df_bottom = df.copy().rename(mapper={'Bottom (cm)': 'depth'}, axis=1).drop(columns=['# Top (cm)'])
        df_top = df.rename(mapper={'# Top (cm)': 'depth'}, axis=1).drop(columns=['Bottom (cm)'])
        df = pd.concat([df_top, df_bottom]).set_index('depth')
        return df


class HandHardnessProfile(LayeredProfile):
    """
    A class for handling hand hardness data. Currently set for only reading a
    custom file but later will read other data
    """
    _text_scale = ['F-', 'F', 'F+',
                   '4F-', '4F', '4F+',
                   '1F-', '1F', '1F+',
                   'P-', 'P', 'P+',
                   'K-', 'K', 'K+', 'I']
    _snowex_column = 'Hand Hardness'

    def __init__(self, **kwargs):
        super(HandHardnessProfile, self).__init__(**kwargs)

    def read_snowpilot(self, filename=None, url=None):
        pass

    def read_simple_text(self, filename):
        """
        Reads in a text file containing only hardness information
        Format is in depth1-depth2:hardness_value
        Args:
            filename: path to the text file
        Returns:
            df: pandas dataframe
        """
        depth = []
        hardness = []
        layer_number = []
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
                    raise ValueError(f"Only one '=' can be used to represent "
                                     f"hand hardness in text file. "
                                     f"On line #{i}.")
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
                    layer_number.append(i)

        df = pd.DataFrame()

        # Check for positive depth
        mn = min(depth)
        mx = max(depth)
        if mx > 0 and mn >= 0:
            self.log.debug('Positive snow height, inverting to negative')
            depth = [d - mx for d in depth]

        for d, h, l in zip(depth, hardness, layer_number):
            data = {'depth': d, 'hardness': h, 'numeric': self.scale[h], 'layer_number': l}
            df = df.append(data, ignore_index=True)

        # Cap the data so it looks good
        # data = {'depth': min(depth), 'hardness': '-', 'numeric': 0}
        df = df.append(data, ignore_index=True)
        return df


class GrainSizeProfile(LayeredProfile):
    _text_scale = ['< 1 mm', '1-2 mm', '2-4 mm', '4-6 mm', '>6 mm']
    _snowex_column = 'Grain Size (mm)'
    def __init__(self, **kwargs):
        super(GrainSizeProfile, self).__init__(**kwargs)
        self._scale = None

class NIRPhotoProfile(GenericProfile):
    """
    Generate a profile using an NIR photo
    """

    def __init__(self, **kwargs):
        super(NIRPhotoProfile, self).__init__(**kwargs)

    def open(self):
        self.img = np.array(Image.open(self.filename))
