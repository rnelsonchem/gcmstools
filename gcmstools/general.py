import os
import shutil

import gcmstools.filetypes as gcf
import gcmstools.reference as gcr
import gcmstools.fitting as gcfit
import gcmstools.datastore as gcd
import gcmstools.calibration as gcc


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
    

def proc_data(data_folder, h5name, nproc=1, filetype='aia', reffile=None,
        fittype=None, calfile=None, **kwargs):
    if filetype == 'aia':
        GcmsObj = gcf.AiaFile
        ends = ('CDF', 'AIA', 'cdf', 'aia') 

    files = os.listdir(data_folder)
    files = [f for f in files if f.endswith(ends)]
    files = [os.path.join(data_folder, f) for f in files]

    ref = None
    if reffile:
        if reffile.endswith(('txt', 'TXT')):
            ref = gcr.TxtReference(reffile, **kwargs)
    
    fit = None
    if fittype:
        if fittype.lower() == 'nnls':
            fit = gcfit.Nnls(**kwargs)

    if nproc == 1:
        datafiles = [GcmsObj(f) for f in files]
        if ref:
            ref(datafiles)
        if fit:
            fit(datafiles)

    h5 = gcd.HDFStore(h5name)
    h5.append_files(datafiles)
    h5.close()

    if calfile:
        cal = gcc.Calibrate(h5name, calfile, **kwargs)
        cal.close()


    
