import os

import numpy as np
import pandas as pd
import tables as tb

class HDFStore(object):
    def __init__(self, hdfname):
        self.hdfname = hdfname
        # Open the HDF file with pandas
        self.pdh5 = pd.HDFStore(hdfname, mode='a', complevel=9,
                complib='blosc')
        # Make a link to the original file as well
        self.h5 = self.pdh5._handle
        # Se up some compression filters
        self._filters = tb.Filters(complevel=9, complib='blosc')
        # These are the columns of my stored DataFrame
        self._files_df_columns = ('name', 'filename')
        
        # Check to see if the 'files' DataFrame is already saved
        if not hasattr(self.h5.root, 'files'):
            # Create a blank DF
            df = pd.DataFrame(columns=self._files_df_columns)
            self.pdh5['files'] = df
        # Reference the DF
        self.files = self.pdh5['files']

        # Check if there is a data group, otherwise create it
        if not hasattr(self.h5.root, 'data'):
            self.h5.create_group('/', 'data', filters=self._filters)

    def append_files(self, datafiles):
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

    def _append(self, name, gcmsobj):
        if hasattr(self.h5.root.data, name):
            different = self._check_data(name, gcmsobj)
            if not different: return
        
        group = self.h5.create_group('/data', name)

        for key, val in gcmsobj.__dict__.items():
            if isinstance(val, np.ndarray):
                self.h5.create_carray(group, key, obj=val,)
            else:
                setattr(group._v_attrs, key, val)

    def _check_data(self, name, obj):
        group = getattr(self.h5.root.data, name)
        groupd = group._v_attrs
        d = obj.__dict__
        for key, val in d.items():
            if isinstance(val, np.ndarray):
                continue
            
            if (not key in groupd) or val != groupd[key]:
                group._f_remove(recursive=True)
                return True

        return False

    def _name_fix(self, badname):
        sp = badname.split('.')
        nosuffix = '_'.join(sp[:-1])
        nospace = nosuffix.replace(' ', '_')
        if nospace[0].isdigit():
            nonum = 'num' + nospcace
            return nonum
        else:
            return nospace

    def close(self, ):
        # Close the hdf file
        self.pdh5.close()
        # Make a copy of the file.
        # This compresses the file if a lot of changes have been made
        tb.copyFile(self.hdfname, self.hdfname+'temp', overwrite=True)
        os.remove(self.hdfname)
        os.rename(self.hdfname+'temp', self.hdfname)

    def recompress(self,):
        # Copy file to recompress
        pass


