import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tables as tb
import scipy.stats as sps

from gcmstools.datastore import HDFStore


class Calibrate(object):
    tblcols = ['Name', 'Start', 'Stop', 'Slope', 'Intercept', 'r', 'p',
            'stderr']

    def __init__(self, h5name, calfile):
        self.h5 = HDFStore(h5name)

        self.caldf = pd.read_csv(calfile)
        gb = self.caldf.groupby('Compound')
        all_calibration_data = []
        for group in gb:
            cal = self._proc_group(group)
            all_calibration_data.append(cal)
        self.h5.pdh5['calibration'] = pd.DataFrame(all_calibration_data,
                columns=Calibrate.tblcols)

        self.h5.pdh5.flush()

    def _proc_group(self, group):
        name, df = group

        integrals = []
        for idx, series in df.iterrows():
            filename = series['File']
            gcms = self.h5.extract_gcms_data(filename)
            integrals.append(gcms.int_extract(name, series))
        integrals = np.array(integrals)

        conc = df['Concentration']

        std = series['Standard']
        has_std = isinstance(std, str) and not std.isspace()
        if has_std:
            stdconc = df['Standard Conc']
            conc = conc/stdconc

        slope, intercept, r, p, stderr = sps.linregress(conc, integrals)

        caldata = [name, series['Start'], series['Stop'], slope, intercept, r,
                p, stderr]

        return caldata

    def close():
        self.h5.close()

