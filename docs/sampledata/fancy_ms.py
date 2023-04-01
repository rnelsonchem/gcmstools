import matplotlib.pyplot as plt

from gcmstools.datastore import GcmsStore

h5 = GcmsStore('data.h5')
data = h5.extract_gcms('data1')
h5.close()

refcpd = 'benzene'
refidx = data.ref_cpds.index(refcpd)

time = 3.07
idx = data.index(data.times, time)

fitspec = data.fit_coef[idx, refidx]*data.ref_array[refidx]
dataspec = data.intensity[idx]

### This is all the plotting stuff

plt.figure(figsize=(10,4))

plt.bar(data.masses, dataspec, width=0.5, fc='b', label="Sample")
plt.bar(data.masses+0.5, fitspec, width=0.5, fc='r', label="Fit")
plt.grid()

plt.xlim(30, 90)
plt.xlabel('m/z')
# Don't show the y-axis ticks
plt.tick_params(axis='y', labelleft=False)
plt.title('Benzene Mass Spectra')

plt.tight_layout()
# We can save files in PDF format, which gives them unlimited resolution.
plt.savefig('fancy_ms.pdf')
