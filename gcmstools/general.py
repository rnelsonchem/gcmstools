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
    

def extract_gcms_data(hdfstore, filename):
    '''Extract a data set from the HDF storage file.'''
    # Find the file info that corresponds to the filename
    mask = hdfstore.files['filename'].str.contains(filename)
    info = hdfstore.files[mask]
    # Check to make sure there aren't too many files selected.
    # This would be very bad
    if len(info) > 1:
        print("Too many files with that name!")
        return None
    info = info.ix[0]

    # Find the group and info that corresponds to this file
    group = getattr(hdfstore.h5.root.data, info['name'])
    gdict = group._v_attrs.gcmsinfo

    # Create a new file object
    # Do not let it process the data
    GcmsObj = getattr(gcf, gdict['file_type'])
    gcms = GcmsObj(filename, file_build=False)

    # Add all of the Python data back
    for key, val in gdict.items():
        setattr(gcms, key, val)
    # Add all the Numpy arrays back
    for child in group:
        setattr(gcms, child.name, child[:])

    return gcms
    
