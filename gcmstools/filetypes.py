import itertools as it

import numpy as np
import netCDF4 as cdf
import pandas as pd


class GcmsFile(object):
    '''Base class for all GCMS files.
    
    This object is meant to be subclassed and can't be instantiated directly.
    Subclasses must define a _ref_file method that extracts the information
    from the reference file.
    '''
    def __init__(self, fname, file_build=True, quiet=False, **kwargs):
        '''
        Arguments
        ---------
        * fname: string - The name of the GCMS data file.
        '''
        self.filename = fname
        if file_build == True:
            if not quiet:
                print("Building: {}".format(fname))
            self._file_proc()

    def index(self, array, *vals, **kwargs):
        if 'axis' in kwargs:
            axis = kwargs['axis']
        else: 
            axis = None

        indices = []
        for val in vals:
            idx = np.abs(val - array).argmin(axis=axis)
            indices.append(idx)

        if len(indices) == 1:
            return indices[0]
        else:
            return np.array(indices, dtype=int)


class AiaFile(GcmsFile):
    '''AIA GCMS File type.

    This subclass reads GCMS data from an AIA (CDF) file type.
    '''
    def __init__(self, *args, **kwargs):
        self.filetype = 'AiaFile'
        super(AiaFile, self).__init__(*args, **kwargs)

    def _groupkey(self, x):
        return x[0]

    def _file_proc(self, ):
        data = cdf.Dataset(self.filename)

        points = data.variables['point_count'][:]

        times_cdf = data.variables['scan_acquisition_time']
        times = times_cdf[:]/60.

        mass_cdf = data.variables['mass_values'][:]
        mass_min = np.int( np.round( mass_cdf.min() ) )
        mass_max = np.int( np.round( mass_cdf.max() ) )
        masses = np.arange(mass_min, mass_max +1)
        
        inten_cdf = data.variables['intensity_values'][:]

        intens = []
        start = 0
        
        for point in points:
            int_zero = np.zeros(masses.size, dtype=float)
            
            if point == 0: 
                intens.append( int_zero )
                continue
                
            mass_tmp = np.round( mass_cdf[start:start+point] ).astype(int)
            ints_tmp = inten_cdf[start:start+point]
            
            mass_tmp2 = []
            ints_tmp2 = []
            for mass, mass_int in it.groupby( zip(mass_tmp, ints_tmp),
                    key=self._groupkey):
                ints = [i[1] for i in mass_int]
                if len(ints) > 1:
                    ints = np.array( ints ).mean()
                else:
                    ints = ints[0]
                mass_tmp2.append(mass)
                ints_tmp2.append(ints)
            mass_tmp2 = np.array(mass_tmp2)
            ints_tmp2 = np.array(ints_tmp2)
                    
            mask = mass_tmp2 - mass_min
            int_zero[mask] = ints_tmp2

            intens.append( int_zero )

            start += point

        data.close()
        
        self.intensity = np.array(intens)
        self.times = times
        self.masses = masses

        self.tic = self.intensity.sum(axis=1)

    def int_extract(self, name, series):
        cpdidx = self.ref_cpds.index(name)
        std = series['Standard']
        has_std = isinstance(std, str) and not std.isspace()
        if has_std:
            stdidx = self.ref_cpds.index(std)

        start = series['Start']
        stop = series['Stop']
        startidx, stopidx = self.index(self.times, start, stop)
        cpdint = self.int_cum[stopidx, cpdidx] - self.int_cum[startidx, cpdidx]
        if has_std:
            stdint = self.int_cum[stopidx, stdidx] - \
                    self.int_cum[startidx, stdidx]
            cpdint = cpdint/stdint

        return cpdint



