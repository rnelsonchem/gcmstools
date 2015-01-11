#from __future__ import unicode_literals

import os
import argparse
import re
from codecs import open
import itertools as it

import numpy as np
import netCDF4 as cdf
import scipy.optimize as spo


#### General Functions ####


def clear_png(folder):
    for f in os.listdir(folder):
        if f[-3:] == 'png':
            os.remove( os.path.join(folder, f) )


def get_args():
    # Get command line values
    parser = argparse.ArgumentParser()

    parser.add_argument('--nproc', default=1,  type=int,
            help='The number of cores to use for processing.')

    # This is a little backwards. If you request no background, this argument
    # gets set to False. That is because of the call to ref_build later.
    parser.add_argument('--nobkg', action='store_const', default=True,
            const=False, help='Turn off the usage of a single  MS slice as a \
            background in fitting.')
    
    parser.add_argument('--bkg_time', default='0.0',  
            help='The time position of the spectrum to use as a background for \
            fitting. This has no effect if "nobkg" is used.' )
    
    parser.add_argument('--ref_name', default='ref_specs.txt',  
            help='The name of the file that contains the reference spectra.')
    
    parser.add_argument('--cal_name', default='cal.h5',  
            help='The name of the calibration HDF file.')
    
    parser.add_argument('--cal_folder', default='calibration',  
            help='The folder that contains the calibration files.')

    parser.add_argument('--data_name', default='data.h5',  
            help='The name of the processed data HDF file.')

    parser.add_argument('--data_folder', default='data',  
            help='The name of folder containing the data files.')
    
    parser.add_argument('--cal_type', default='conc',  
            help='The type of calibration that was done for these samples. \
            conc = Typical concentration curve; internal = internal standard.')

    parser.add_argument('--standard', default='octane',  
            help='The internal standard used for calibration. Only used if \
            cal_type == "internal".')

    parser.add_argument('--std_start', default=7.0,  type=float,
            help='The start time for integration of the internal standard. \
            Only valid if cal_type == "internal".')

    parser.add_argument('--std_stop', default=7.4,  type=float,
            help='The stop time for integration of the internal standard. \
            Only valid if cal_type == "internal".')

    return parser.parse_args()


def table_check(table, args):
    # Warn if background info is not the same for calibrations and data analysis
    if table.attrs.bkg != args.nobkg:
        if table.attrs.bkg == True:
            print \
'''Warning: Your calibration data was run with a background subtraction. 
This may affect the analysis values.
'''

        else:
            print \
'''Warning: Your calibration data was not run with a background subtraction.
This may affect the analysis values.
'''

    elif table.attrs.bkg_time != args.bkg_time:
        warning = \
'''Warning: The time for your background spectrum does not match the
calibration data. This may affect the values of your analysis.
Calibration background time = {}
Data background time = {}
'''
        print warning.format(table.attrs.bkg_time, args.bkg_time)
    
    if table.attrs.cal_type == 'internal' or args.cal_type == 'internal':
        if table.attrs.cal_type != args.cal_type:
            warning =  \
'''The calibration types do not match!
Current selection: {}
Used for calibration: {}
Type changed to saved value from calibration data.
'''
            print warning.format(args.cal_type, table.attrs.cal_type)
            args.cal_type = table.attrs.cal_type
        
        if table.attrs.std_start != args.std_start or \
                table.attrs.std_stop != args.std_stop:
            warning = \
'''Internal standard integration times are mismatched.
Cal start {:.3f}: Selected Start {:.3f}
Cal stop  {:.3f}: Selected Stop {:.3f}
Values changed to saved values from calibration data.
'''
            print warning.format(table.attrs.std_start, args.std_start,
                    table.attrs.std_stop, args.std_stop)
            args.std_start = table.attrs.std_start
            args.std_stop = table.attrs.std_stop
    


