import os

import numpy as np
import pandas as pd
import tables as tb

import gcmstools.filetypes as gcf

class HDFStore(object):
    def __init__(self, hdfname):
        self.hdfname = hdfname
        # Open the HDF file with pandas
        self.pdh5 = pd.HDFStore(hdfname, mode='a', complevel=9,
                complib='blosc')
        # Make a link to the original file as well
        self.tbh5 = self.pdh5._handle
        # Se up some compression filters
        self._filters = tb.Filters(complevel=9, complib='blosc')
        # These are the columns of my stored DataFrame
        self._files_df_columns = ('name', 'filename')
        
        # Check to see if the 'files' DataFrame is already saved
        if not hasattr(self.pdh5, 'files'):
            # Create a blank DF
            df = pd.DataFrame(columns=self._files_df_columns)
            self.pdh5['files'] = df
        # Reference the DF
        self.files = self.pdh5['files']

        # Check if there is a data group, otherwise create it
        if not hasattr(self.tbh5.root, 'data'):
            self.tbh5.create_group('/', 'data', filters=self._filters)
        self.data = self.tbh5.root.data

    def append_files(self, datafiles):
        '''Append a series of GCMS files into the HDF container.'''
        # Make sure datafiles is iterable
        if not isinstance(datafiles, (tuple, list)):
            datafiles = [datafiles,]
        
        names = []
        for data in datafiles:
            filename = data.filename
            name = self._name_fix(filename)
            names.append((name, filename))
            self._append(name, data)
        temp_df = pd.DataFrame(names, columns=self._files_df_columns)\

        self.pdh5['files'] = pd.merge(temp_df, self.pdh5['files'],
                how='outer')
        self.files = self.pdh5.files

        self.pdh5.flush()

    def extract_gcms_data(self, filename):
        '''Extract a data set from the HDF storage file.'''
        # Find the file info that corresponds to the filename
        mask = self.files['filename'].str.contains(filename)
        info = self.files[mask]
        # Check to make sure there aren't too many files selected.
        # This would be very bad
        if len(info) > 1:
            print("Too many files with that name!")
            return None
        elif len(info) == 0:
            print("No files with name {}".format(filename))
        info = info.iloc[0]
    
        # Find the group and info that corresponds to this file
        group = getattr(self.data, info['name'])
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
    
    def close(self, ):
        # Close the hdf file
        self.pdh5.close()
        # Make a copy of the file.
        # This compresses the file if a lot of changes have been made
        tb.copyFile(self.hdfname, self.hdfname+'temp', overwrite=True)
        os.remove(self.hdfname)
        os.rename(self.hdfname+'temp', self.hdfname)

    def _append(self, name, gcmsobj):
        '''Append a single GCMS file into the HDF container.'''
        # If this exists already, check for equivalence
        if hasattr(self.data, name):
            different = self._check_data(name, gcmsobj)
            if not different: return
       
        # If not equivalent add the data set to the file
        group = self.tbh5.create_group('/data', name)

        # Run through the items in the GCMS file
        # Create an info dict for recreating object
        gcmsinfo = {}
        for key, val in gcmsobj.__dict__.items():
            # If they are Numpy arrays, add CArray
            if isinstance(val, np.ndarray):
                self.tbh5.create_carray(group, key, obj=val,)
            # Or else, set a group attribute with the value
            # This is used to check if any changes have been made
            else:
                gcmsinfo[key] = val
        group._v_attrs['gcmsinfo'] = gcmsinfo

    def _check_data(self, name, obj):
        '''Check for equivalence between GCMS file and stored data.'''
        group = getattr(self.data, name)
        groupd = group._v_attrs.gcmsinfo
        d = obj.__dict__
        for key, val in d.items():
            # Ignore the arrays for now
            if isinstance(val, np.ndarray):
                continue
            # Check the other values agains the group attributes
            # If there is a mismatch, return True
            if (not key in groupd) or val != groupd[key]:
                # Remove old data
                group._f_remove(recursive=True)
                return True
        # No mismatch
        return False

    def _name_fix(self, badname_path):
        '''Remove special characters from filename.

        This is necessary for PyTables natural naming, which is very
        convenient. 
        '''
        pth, badname = os.path.split(badname_path)
        sp = badname.split('.')
        nosuffix = '_'.join(sp[:-1])
        nospace = nosuffix.replace(' ', '_')
        if nospace[0].isdigit():
            nonum = 'num' + nospcace
            return nonum
        else:
            return nospace


