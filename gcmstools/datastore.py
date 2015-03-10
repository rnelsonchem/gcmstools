import os

import numpy as np
import pandas as pd
import tables as tb

import gcmstools.filetypes as gcf

class GcmsStore(pd.HDFStore):
    def __init__(self, hdfname, quiet=False, **kwargs):
        if not 'mode' in kwargs:
            kwargs['mode'] = 'a'
        if not 'complevel' in kwargs:
            kwargs['complevel'] = 9
        if not 'complib' in kwargs:
            kwargs['complib'] = 'blosc'
        super(GcmsStore, self).__init__(hdfname, **kwargs)

        self._quiet = quiet

        # These are the columns of my stored DataFrame
        self._files_df_columns = ('name', 'filename')
        
        # Check if there is a data group, otherwise create it
        if not hasattr(self._handle.root, 'data'):
            self._handle.create_group('/', 'data', filters=self._filters)
        self.data = self._handle.root.data

    def append_gcms(self, datafiles):
        '''Append a series of GCMS files into the HDF container.'''
        # Make sure datafiles is iterable
        if not isinstance(datafiles, (tuple, list)):
            datafiles = [datafiles,]
        
        names = []
        for data in datafiles:
            filename = data.filename
            name = self._gcms_name_fix(filename)
            names.append((name, filename))
            self._append_single_gcms(name, data)
        temp_df = pd.DataFrame(names, columns=self._files_df_columns)\

        if not hasattr(self, 'files'):
            self.put('files', temp_df)
        else:
            self.put('files', pd.merge(temp_df, self.files,
                    how='outer'))

        self.flush()

    def extract_gcms(self, filename):
        '''Extract a data set from the HDF storage file.'''
        name = self._gcms_name_fix(filename)
    
        # Find the group and info that corresponds to this file
        group = getattr(self.data, name)
        gdict = group._v_attrs.gcmsinfo
    
        # Create a new file object
        # Do not let it process the data
        GcmsObj = getattr(gcf, gdict['filetype'])
        gcms = GcmsObj(filename, file_build=False)
    
        # Add all of the Python data back
        for key, val in gdict.items():
            setattr(gcms, key, val)
        # Add all the Numpy arrays back
        for child in group:
            setattr(gcms, child.name, child[:])

        gcms.shortname = name
    
        return gcms
    
    def compress(self, ):
        '''Close and compress the HDF file after creation.'''
        # Close the hdf file
        self.close()
        # Make a copy of the file.
        # This compresses the file if a lot of changes have been made
        tb.copyFile(self.filename, self.filename+'temp', overwrite=True)
        os.remove(self.filename)
        os.rename(self.filename+'temp', self.filename)

    def _append_single_gcms(self, name, gcmsobj):
        '''Append a single GCMS file into the HDF container.'''
        # If this exists already, check for equivalence
        if hasattr(self.data, name):
            different = self._check_gcms_data(name, gcmsobj)
            if not different: 
                if not self._quiet:
                    print("HDF Skipping: {}".format(name))
                return
       
        if not self._quiet:
            print("HDF Appending: {}".format(name))
        # If not equivalent add the data set to the file
        group = self._handle.create_group('/data', name, 
                filters=self._filters)

        # Run through the items in the GCMS file
        # Create an info dict for recreating object
        gcmsinfo = {}
        for key, val in gcmsobj.__dict__.items():
            # If they are Numpy arrays, add CArray
            if isinstance(val, np.ndarray):
                self._handle.create_carray(group, key, obj=val,)
            # Or else, set a group attribute with the value
            # This is used to check if any changes have been made
            else:
                gcmsinfo[key] = val
        group._v_attrs['gcmsinfo'] = gcmsinfo

    def _check_gcms_data(self, name, obj):
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
                if not self._quiet:
                    print("HDF Removing: {}".format(name))
                # Remove old data
                group._f_remove(recursive=True)
                return True
        # No mismatch
        return False

    def _gcms_name_fix(self, badname_path):
        '''Remove special characters from filename.

        This is necessary for PyTables natural naming, which is very
        convenient. 
        '''
        pth, badname = os.path.split(badname_path)
        sp = badname.split('.')
        if len(sp) > 1:
            nosuffix = '_'.join(sp[:-1])
        else:
            nosuffix = sp[0]
        nohyp = nosuffix.replace('-', '_')
        nospace = nohyp.replace(' ', '_')
        if nospace[0].isdigit():
            nonum = 'num' + nospace
            return nonum
        else:
            return nospace


