import os
import sys
sys.stdout.flush()
import glob
import obspy
import scipy
import pyasdf
import numpy as np
import yaml
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, DayLocator, MonthLocator
from scipy.fftpack import next_fast_len
from obspy.signal.filter import bandpass
from matplotlib.ticker import MultipleLocator
import pandas as pd

# PARAMETER SECTION
DATADIR = '/srv/beegfs/scratch/shares/cdff/DPM/Processing/STACK_SS_1bit_no_bad_stations' 
freqmin = 0.1
freqmax = 1.0
component = 'ZZ'
OUTDIR = '/srv/beegfs/scratch/shares/cdff/DPM/mika_scripts/stack_all_plotting/plots'
def plot_substack_all(sfile, freqmin, freqmax, ccomp, disp_lag=None, savefig=False, sdir=None, figsize=(14, 14)):
    '''
    display the 2D matrix of the cross-correlation functions stacked for all time windows.

    PARAMETERS:
    ---------------------
    sfile: cross-correlation functions outputed by S2
    freqmin: min frequency to be filtered
    freqmax: max frequency to be filtered
    disp_lag: time ranges for display
    ccomp: cross component of the targeted cc functions

    USAGE: 
    ----------------------
    plot_substack_all('temp.h5',0.1,1,'ZZ',50,True,'./')
    '''
    # open data for read
    if savefig:
        if sdir == None: print('no path selected! save figures in the default path')

    paths = ccomp
    try:
        ds = pyasdf.ASDFDataSet(sfile, mode='r')
        # extract common variables
        dtype_lists = ds.auxiliary_data.list()
        dt = ds.auxiliary_data[dtype_lists[0]][paths].parameters['dt']
        dist = ds.auxiliary_data[dtype_lists[0]][paths].parameters['dist']
        maxlag = ds.auxiliary_data[dtype_lists[0]][paths].parameters['maxlag']
    except Exception:
        print("exit! cannot open %s to read" % sfile);
        sys.exit()

    if len(dtype_lists) == 1:
        raise ValueError('Abort! seems no substacks have been done')

    # lags for display   
    if not disp_lag: disp_lag = maxlag
    if disp_lag > maxlag: raise ValueError('lag excceds maxlag!')
    t = np.arange(-int(disp_lag), int(disp_lag) + dt, step=int(2 * int(disp_lag) / 4))
    indx1 = int((maxlag - disp_lag) / dt)
    indx2 = indx1 + 2 * int(disp_lag / dt) + 1

    # other parameters to keep
    num_stacks = len([itype for itype in dtype_lists if "stack" in itype])
    nwin = len(dtype_lists) - num_stacks
    data = np.zeros(shape=(nwin, indx2 - indx1), dtype=np.float32)
    ngood = np.zeros(nwin, dtype=np.int16)
    ttime = np.zeros(nwin, dtype=np.int)
    timestamp = np.empty(ttime.size, dtype='datetime64[s]')
    amax = np.zeros(nwin, dtype=np.float32)

    for ii, itype in enumerate(dtype_lists[num_stacks:]):
        if "Allstack" in itype: continue
        timestamp[ii] = obspy.UTCDateTime(np.float(itype[1:]))
        try:
            ngood[ii] = ds.auxiliary_data[itype][paths].parameters['ngood']
            ttime[ii] = ds.auxiliary_data[itype][paths].parameters['time']
            data[ii] = ds.auxiliary_data[itype][paths].data[indx1:indx2]
            
            if data[ii].size == 0:
                print(f"No data extracted for {itype}. Skipping.")
                continue
            
            data[ii] = bandpass(data[ii], freqmin, freqmax, int(1 / dt), corners=4, zerophase=True)
            
            if data[ii].size == 0:
                print(f"Bandpass filtering resulted in empty data for {itype}. Skipping.")
                continue
            
            amax[ii] = np.max(data[ii])
            data[ii] /= amax[ii]
            
        except Exception as e:
            print(f"Error in file {sfile}, timestamp {timestamp[ii]}: {e}")
            continue


#     for ii, itype in enumerate(dtype_lists[num_stacks:]):
#         if "Allstack" in itype: continue
#         timestamp[ii] = obspy.UTCDateTime(np.float(itype[1:]))
#         try:
#             ngood[ii] = ds.auxiliary_data[itype][paths].parameters['ngood']
#             ttime[ii] = ds.auxiliary_data[itype][paths].parameters['time']
#             # timestamp[ii] = obspy.UTCDateTime(ttime[ii])
#             # cc matrix
#             data[ii] = ds.auxiliary_data[itype][paths].data[indx1:indx2]
#             data[ii] = bandpass(data[ii], freqmin, freqmax, int(1 / dt), corners=4, zerophase=True)
#             amax[ii] = np.max(data[ii])
#             data[ii] /= amax[ii]
#         except Exception as e:
#             #             print(e)
#             continue

        if len(ngood) == 1:
            raise ValueError('seems no substacks have been done! not suitable for this plotting function')

    # plotting
    if nwin > 100:
        tick_inc = int(nwin / 10)
    elif nwin > 10:
        tick_inc = int(nwin / 5)
    else:
        tick_inc = 2
    fig, ax = plt.subplots(2, sharex=False, figsize=figsize)
    ax[0].matshow(data, cmap='seismic', extent=[-disp_lag, disp_lag, nwin, 0], aspect='auto')
    ax[0].set_title('%s dist:%5.2f km filtered at %4.2f-%4.2fHz' % (sfile.split('/')[-1], dist, freqmin, freqmax))
    ax[0].set_xlabel('time [s]')
    ax[0].set_ylabel('wavefroms')
    ax[0].set_xticks(t)
    ax[0].set_yticks(np.arange(0, nwin, step=tick_inc))
    ax[0].set_yticklabels(timestamp[0:nwin:tick_inc])
    ax[0].xaxis.set_ticks_position('bottom')
    ax[0].axvline(0, color="k", ls=":", lw=2)
    ax[1].plot(amax / max(amax), 'r-')
    ax2 = ax[1].twinx()
    ax2.plot(ngood, 'b-')
    ax2.set_ylabel('ngood', color="b")
    ax[1].set_ylabel('relative amp', color="r")
    ax[1].set_xlabel('waveform number')
    ax[1].set_xticks(np.arange(0, nwin, nwin // 5))
    ax[1].legend(['relative amp', 'ngood'], loc='upper right')
    # save figure or just show
    if savefig:
        if sdir == None: sdir = sfile.split('.')[0]
        if not os.path.isdir(sdir): os.mkdir(sdir)
        outfname = sdir + '/{0:s}_{1:4.2f}_{2:4.2f}Hz.pdf'.format(sfile.split('/')[-1], freqmin, freqmax)
        fig.savefig(outfname, format='png', dpi=300)
        print(f'Saving figure in {outfname}')
        plt.close()
    else:
        plt.show()  # GS

# Loop over files to check them out
sdir = glob.glob(os.path.join(DATADIR, '*', '*.h5'))
sdir.sort()
for sfile in sdir:
    print(f"Processing this file: {sfile}")
    try:
        plot_substack_all(sfile=sfile, freqmin=freqmin, freqmax=freqmax, ccomp=ccomp, disp_lag=50, savefig=True, sdir=sdir)
    except Exception as e:
            print(f"Skipping {sfile} due to an error: {e}")
            continue
