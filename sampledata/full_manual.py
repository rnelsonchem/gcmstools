import os

from gcmstools.filetypes import AiaFile
from gcmstools.reference import TxtReference
from gcmstools.fitting import Nnls
from gcmstools.datastore import GcmsStore
from gcmstools.calibration import Calibrate

datafolder = 'folderwithdata/'

files = os.listdir(datafolder)
cdfs = [os.path.join(datafolder, f) for f in files if f.endswith('CDF')] 

ref = TxtReference('ref_specs.txt')
fit = Nnls()
h5 = GcmsStore('data.h5')

for cdf in cdfs:
    data = AiaFile(cdf) 
    ref(data)
    fit(data)
    h5.append_gcms(data)
h5.close()

cal = Calibrate()
cal.curvegen('calibration.csv')
cal.datagen()
cal.close()


