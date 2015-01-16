import os
from multiprocessing import Pool

import numpy as np
import tables as pyt
import matplotlib.pyplot as plt

#import chem.gcms as gcms
import gcms

# Get the command line arguments
args = gcms.get_args()

# This function is from: http://stackoverflow.com/questions/434287
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))


def aia_proc(fname, args=args):
    print 'Processing:', fname
    aia = gcms.AIAFile( os.path.join(args.data_folder, fname) )
    aia.ref_build(args.ref_name, bkg=args.nobkg,
            bkg_time=float(args.bkg_time) )
    aia.nnls()

    if args.cal_type == 'internal':
        aia.integrate(args.std_start, args.std_stop)
        n = aia.ref_files.index( args.standard )
        aia.std_int = aia.integral[n]
        
        mask = aia.last_int_mask
        plt.plot(aia.times[mask], aia.last_int_sim[:,n])
        plt.plot(aia.times[mask], aia.tic[mask], 'k', lw=1.5)
        plt.savefig( 
                os.path.join(args.data_folder, fname[:-4]+'_intstd'), 
                dpi=200 )
        plt.close()

    return aia

# Open the calibration data file
cal = pyt.openFile(args.cal_name)
cal_table = cal.root.cals

gcms.table_check(cal_table, args)

# Make a new hdf5 file for data from sample runs
h5f = pyt.openFile(args.data_name, 'w', 'Catalytic Runs')

cal_cpds = [i[0] for i in cal_table]
col_dict = {cal_cpd: pyt.Float64Col() for cal_cpd in cal_cpds}
col_dict['fname'] = pyt.StringCol(255, pos=0)

col_dict2 = col_dict.copy()
for cal_cpd in cal_cpds:
    col_dict2[ cal_cpd+'_per' ] = pyt.Float64Col()
col_dict2['cpd_name'] = pyt.StringCol(255, pos=1)

int_table = h5f.createTable('/', 'int_data', col_dict2, 
        "Raw Integration Data")
int_table.attrs.bkg = args.nobkg
int_table.attrs.bkg_time = args.bkg_time

data_table = h5f.createTable('/', 'conc_data', col_dict, 
        "Concentration Data")


files = os.listdir(args.data_folder)
files = [f for f in files if f[-3:] == 'CDF']
if args.cal_type == 'internal':
    std_cons = {}
    f = open('data.csv')
    next(f)
    for line in f:
        if line[0] == '#': continue
        elif line.isspace(): continue
        sp = line.split(',')
        std_cons[sp[0]] = float(sp[1])
    f.close()


gcms.clear_png(args.data_folder)


if args.nproc > 1:
    pool = Pool(args.nproc)

for fs in chunker(files, args.nproc):
    if args.nproc > 1:
        aias = pool.map(aia_proc, fs)
    else:
        aias = [ aia_proc(fs[0]), ]

    for aia in aias:
        f = os.path.split(aia.filename)[-1]
        name = f[:-4]
    
        row = data_table.row
        row['fname'] = name
    
        for cpd in cal_table:
            cpd_name = cpd[0]
            start, stop = cpd[1], cpd[2]
            slope, intercept = cpd[3], cpd[4]
            column = cpd[8]
    
            aia.integrate( start, stop )
            ints = aia.integral
            ints_sum = ints.sum()
            int_row = int_table.row
            int_row['fname'] = name
            int_row['cpd_name'] = cpd_name
    
            for n, cal_cpd in enumerate(cal_cpds):
                int_row[ cal_cpd ] = ints[n]
                int_row[ cal_cpd+'_per' ] = ints[n]/ints_sum
            int_row.append()
            
            if args.cal_type == 'internal':
                int_adj = ints[column]/aia.std_int
                conc = (int_adj - intercept)/slope
                conc = conc*std_cons[f]
            else:
                conc = (ints[column] - intercept)/slope

            row[ cpd_name ] = conc
   
            mask = aia.last_int_mask
            plt.plot(aia.times[mask], aia.last_int_sim[:,column])
            plt.plot(aia.times[mask], aia.tic[mask], 'k', lw=1.5)
            plt.title('Concentration = {:.2f}'.format(conc))
            plt.savefig( 
                    os.path.join(args.data_folder, name+'_'+cpd_name), 
                    dpi=200 )
            plt.close()
    
        row.append()
        h5f.flush()

cal.close()
h5f.close()

pyt.copyFile(args.data_name, args.data_name+'temp', overwrite=True)
os.remove(args.data_name)
os.rename(args.data_name+'temp', args.data_name)
