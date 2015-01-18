import os
import shutil
import sys

from IPython.parallel import Client, interactive

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
    

def proc_data(data_folder, h5name, multiproc=False, chunk_size=4,
        filetype='aia', reffile=None, fittype=None, calfile=None,
        picts=False, **kwargs):

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

    h5 = gcd.HDFStore(h5name, **kwargs)

    if multiproc:
        try:
            client = Client()
        except:
            error = "ERROR! You do not have an IPython Cluster running.\n\n"
            error += "Start cluster with: ipcluster start -n # &\n"
            error += "Where # == the number of processors.\n\n"
            error += "Stop cluster with: ipcluster stop"
            print(error)
            h5.close()
            return 

        dview = client[:]
        dview.block = True
        dview['ref'] = ref
        dview['fit'] = fit
        dview['GcmsObj'] = GcmsObj
        chunk_size = len(dview)

    # Chunk the data so lots of data files aren't opened in memory.
    for chunk in _chunker(files, chunk_size):
        if multiproc:
            datafiles = dview.map_sync(_proc_file, 
                    [(i, kwargs) for i in chunk])
        else:
            datafiles = [GcmsObj(f, **kwargs) for f in chunk]
            if ref:
                ref(datafiles)
            if fit:
                fit(datafiles)

        h5.append_files(datafiles)

    if calfile:
        cal = gcc.Calibrate(h5, **kwargs)
        cal.curvegen(calfile, picts=picts, **kwargs)
        cal.datagen(picts=picts, **kwargs)

    h5.close()

# This function is from: http://stackoverflow.com/questions/434287
def _chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

# This function is for the multiproc version.
# Must use the interactive decorator to update the node namespace
@interactive
def _proc_file(file_kwargs):
    filename, kwargs = file_kwargs
    datafile = GcmsObj(filename, **kwargs)
    if ref:
        ref(datafile)
    if fit:
        fit(datafile)
    return datafile


