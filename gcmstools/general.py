import os
import shutil

import netCDF4 as cdf

import filetypes
import reference
import fitting


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
    

def open_file(fname, refs=None, fit=None):
    '''Function to construct GCMS file object.

    Arguments
    ---------
    * fname: string - The name of the GCMS data file.
    * refs: string - The name of a reference file for fitting.
    * fit: string - The type of fitting to use on the data.
        - 'nnls': non-negative least squares
    '''
    objects = []
    names = []
    reconstruct = [fname,]

    filetype = fname[-3:].lower()
    if filetype == 'cdf':
        objects.append(filetypes.AIAFile)
   
    if refs:
        reconstruct.append( refs )
        reffiletype = refs[-3:].lower()
        if reffiletype == 'txt':
            objects.append(reference.TxtReference)
        if reffiletype == 'msl':
            objects.append(reference.MslReference)

    if fit:
        fit = fit.lower()
        reconstruct.append( fit )
        if fit == 'nnls':
            objects.append(fitting.Nnls)

    # This is a constructor for the dynamic GCMS class
    newobj = filetypes.GcmsMeta('Gcms', tuple(objects), {})
    instance = newobj(fname, refs)
    instance._reconstruct = reconstruct
    if refs:
        instance._ref_file = refs
    return instance
