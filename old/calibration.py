import os
import argparse
from multiprocessing import Pool

import numpy as np
import tables as pyt
import scipy.stats as sps
import matplotlib.pyplot as plt

#import chem.gcms as gcms
import gcms

# Get the command line arguments
args = gcms.get_args()

def cal_h5_build(args):
    class CalTable( pyt.IsDescription ):
        cpd = pyt.StringCol( 50, pos=0 )
        int_start = pyt.Float64Col( pos=1 )
        int_stop = pyt.Float64Col( pos=2 )
        slope = pyt.Float64Col( pos=3 )
        intercept = pyt.Float64Col( pos=4 )
        r = pyt.Float64Col( pos=5 )
        p = pyt.Float64Col( pos=6 )
        stderr = pyt.Float64Col( pos=7 )
        refcol = pyt.Int16Col( pos=8 )
        
    h5f = pyt.openFile(args.cal_name, 'w', 'GCMS Calibrations')
    table = h5f.createTable('/', 'cals', CalTable, )

    # Here I'm storing the background information in case I need to know
    # later.
    table.attrs.bkg = args.nobkg
    table.attrs.bkg_time = args.bkg_time
    table.attrs.cal_type = args.cal_type
    if args.cal_type == 'internal':
        table.attrs.standard = args.standard
        table.attrs.std_start = args.std_start
        table.attrs.std_stop = args.std_stop

    return h5f, table

def cal_file(fname):
    f = open(fname)
    next(f)
    
    refs = {}
    ref_files = set()
    for line in f:
        if line[0] == '#': continue
        elif line.isspace(): continue
        line = line.strip()

        sp = line.split(',')
        if sp[0] in refs:
            refs[ sp[0] ].append(sp[1:])
        else:
            refs[ sp[0] ] = [ sp[1:], ]
        ref_files.add(sp[1])

    return refs, list(ref_files)

def aia_build(ref_file, args=args):
    print 'Processing:', ref_file

    aia = gcms.AIAFile( os.path.join(args.cal_folder, ref_file) )

    aia.ref_build(args.ref_name, bkg=args.nobkg,
            bkg_time=float(args.bkg_time))

    aia.nnls()

    if args.cal_type == 'internal':
        aia.integrate(args.std_start, args.std_stop)
        n = aia.ref_files.index( args.standard )
        aia.std_int = aia.integral[n]
        
        mask = aia.last_int_mask
        plt.plot(aia.times[mask], aia.tic[mask], 'k', lw=2)
        plt.plot(aia.times[mask], aia.last_int_sim[:,n])
        plt.savefig( os.path.join(args.cal_folder, ref_file[:-4]+'_std'), 
                dpi=200)
        plt.close()

    return aia

def int_extract(name, info, aias, args):
    ints = []
    conc = []
    if args.cal_type == 'internal':
        stdint = []
        stdcon = []

    plt.figure()
    for line in info:
        aia = aias[ line[0] ]

        start, stop = [float(i) for i in line[2:4]]
        n = aia.ref_files.index(name)
        aia.integrate(start, stop)

        conc.append( line[1] )
        ints.append( aia.integral[n] )
        
        mask = aia.last_int_mask
        plt.plot(aia.times[mask], aia.last_int_sim[:,n])

        if args.cal_type == 'internal':
            stdcon.append( line[4] )
            stdint.append( aia.std_int )

    plt.xlim(start, stop)
    plt.savefig(os.path.join(args.cal_folder, name+'_'+'fits'), dpi=200)
    plt.close()

    ints = np.array(ints, dtype=float)
    conc = np.array(conc, dtype=float)
    if args.cal_type == 'internal':
        stdint = np.array(stdint, dtype=float)
        stdcon = np.array(stdcon, dtype=float)
        ints = ints/stdint
        conc = conc/stdcon

    slope, intercept, r, p, stderr = sps.linregress(conc, ints)
    cal_plot(name, args, ints, conc, slope, intercept, r)

    row = table.row
    row['cpd'] = name
    row['int_start'] = start
    row['int_stop'] = stop
    row['slope'] = slope
    row['intercept'] = intercept
    row['r'] = r
    row['p'] = p
    row['stderr'] = stderr
    row['refcol'] = n
    row.append()


def cal_plot(name, args, ints, conc, slope, intercept, r):
    plt.figure()
    plt.plot(conc, slope*conc + intercept, 'k-')
    plt.plot(conc, ints, 'o', ms=8)
    text_string = 'Slope: {:.2f}\nIntercept: {:.2f}\nR^2: {:.5f}'
    plt.text(0.5, ints.max()*0.8, text_string.format(slope, intercept, r**2))
    plt.savefig(os.path.join(args.cal_folder, name+'_cal_curve'), dpi=200)
    plt.close()


if __name__ == '__main__':
    h5f, table = cal_h5_build(args)

    refs, ref_files = cal_file('calibration.csv')

    gcms.clear_png(args.cal_folder)

    if args.nproc == 1:
        aias = [aia_build(i) for i in ref_files]
    else:
        p = Pool(args.nproc)
        aias = p.map(aia_build, ref_files)

    aias = dict( zip(ref_files, aias) )

    for name in refs:
        int_extract(name, refs[name], aias, args)
        h5f.flush()

    h5f.close()
    
    pyt.copyFile(args.cal_name, args.cal_name+'temp', overwrite=True)
    os.remove(args.cal_name)
    os.rename(args.cal_name+'temp', args.cal_name)

