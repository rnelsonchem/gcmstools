import numpy as np
import pandas as pd
import tables as tb

class HDFStore(object):
    def __init__(self, hdfname):
        # Open the HDF file with pandas
        self.pdh5 = pd.HDFStore(hdfname, mode='a', complevel=9,
                complib='blosc')
        # Make a link to the original file as well
        self.h5 = self.pdh5._handle
        # Se up some compression filters
        self._filters = tb.Filters(complevel=9, complib='blosc')
        # These are the columns of my stored DataFrame
        self._files_df_columns = ('name', 'filenames')
        
        # Check to see if the 'files' DataFrame is already saved
        if not hasattr(self.h5.root, 'files'):
            # Create a blank DF
            df = pd.DataFrame(columns=self._files_df_columns).set_index('name')
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
                .set_index('name')

        self.pdh5['files'] = pd.concat( (self.pdh5['files'], temp_df) )

    def _append(self, name, gcmsobj):
        group = self.h5.create_group('/data', name)

        for key, val in gcmsobj.__dict__.items():
            if isinstance(val, np.ndarray):
                self.h5.create_carray(group, key, obj=val,)
            else:
                setattr(group._v_attrs, key, val)

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
        self.pdh5.close()

    def recompress(self,):
        # Copy file to recompress
        pass


