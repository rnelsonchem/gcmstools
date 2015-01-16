import os
import shutil

import netCDF4 as cdf

import gcmstools.filetypes as gcf
import gcmstools.reference
import gcmstools.fitting


_ROOT = os.path.abspath(os.path.dirname(__file__))
_PWD = os.getcwd()

def get_sample_data(fname=None):
    '''Copy sample data to current folder.

    Use this function to copy sample data from the gcmstools package directory
    into the current folder. Found this solution on this StackOverflow
    question:
    http://stackoverflow.com/questions/4519127

    Arguments
    ----------

    * *fname* -- ``None`` (default) or string. If None, all sample files are
    copied to the current directory. Otherwise, a single filename string
    can be passed in order to copied to the current folder.
    '''
    data_dir = os.path.join(_ROOT, 'sampledata')
    if fname == None:
        fnames = os.listdir(data_dir)
    elif isinstance(fname, str):
        fnames = [fname,]
    else:
        raise ValueError("Your filename must be a string or None.")

    [shutil.copy(os.path.join(data_dir, name), os.path.join(_PWD, name)) for
            name in fnames]
    

