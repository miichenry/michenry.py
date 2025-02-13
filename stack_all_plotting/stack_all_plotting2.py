import os
import sys
import glob
import pyasdf
import numpy as np
import yaml
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from obspy.signal.filter import bandpass

# PARAMETER SECTION
config_file = sys.argv[1]
with open(config_file, 'r') as file:
    para = yaml.safe_load(file)

print("Loaded Configuration:")
print(para)

# data/file paths
DATADIR = para['DATADIR']
freqmin = para['freqmin']       
freqmax = para['freqmax']
ccomp = para['component']
sdir = para['OUTDIR']

def plot_substack_all(sfile, freqmin, freqmax, ccomp, disp_lag=None, savefig=False, sdir=None, figsize=(14, 14)):
    '''
    Display the 2D matrix of the cross-correlation functions stacked for all time windows.

    PARAMETERS:
    ---------------------
    sfile: cross-correlation functions outputted by S2
    freqmin: min frequency to be filtered
    freqmax: max frequency to be filtered
    disp_lag: time ranges for display
    ccomp: cross component of the targeted cc functions
    '''
    # Open data for read
    if savefig:
        if sdir is None: print('No path selected! Saving figures in the default path')

    try:
        ds = pyasdf.ASDFDataSet(sfile, mode='r')
        dtype_lists = ds.auxiliary_data.list()
        print(f'dtype_list = {dtype_lists}')
        paths = ccomp
        dt = ds.auxiliary_data[dtype_lists[0]][paths].parameters['dt']
        dist = ds.auxiliary_data[dtype_lists[0]][paths].parameters['dist']
        maxlag = ds.auxiliary_data[dtype_lists[0]][paths].parameters['maxlag']
    except Exception as e:
        print(f"Error opening file {sfile}: {e}")
        return

    if len(dtype_lists) == 1:
        raise ValueError('No substacks found')

    if not disp_lag:
        disp_lag = maxlag
    if disp_lag > maxlag:
        raise ValueError('disp_lag exceeds maxlag!')

    t = np.arange(-int(disp_lag), int(disp_lag) + dt, step=int(2 * int(disp_lag) / 4))
    indx1 = int((maxlag - disp_lag) / dt)
    indx2 = indx1 + 2 * int(disp_lag / dt) + 1

    num_stacks = len([itype for itype in dtype_lists if "stack" in itype])
    print(f'numstacks = {num_stacks}')
    nwin = len(dtype_lists) - num_stacks
    print(f'nwin = {nwin}')
    data = np.zeros(shape=(nwin, indx2 - indx1), dtype=np.float32)
    ngood = np.zeros(nwin, dtype=np.int16)
    ttime = np.zeros(nwin, dtype=np.int)
    timestamp = np.empty(ttime.size, dtype='datetime64[s]')
    amax = np.zeros(nwin, dtype=np.float32)

    for ii, itype in enumerate(dtype_lists[num_stacks:]):
        if "Allstack" in itype:
            continue
        try:
            timestamp[ii] = obspy.UTCDateTime(float(itype[1:]))
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
            print(f"Error processing {itype}: {e}")
            continue

    if nwin == 0:
        print(f"No valid windows for file {sfile}.")
        return

    # Plotting
    fig, ax = plt.subplots(2, sharex=False, figsize=figsize)
    
    if data.size > 0:
        im = ax[0].matshow(data, cmap='seismic', extent=[-disp_lag, disp_lag, nwin, 0], aspect='auto')
        ax[0].set_title(f'{sfile.split("/")[-1]} dist:{dist:.2f} km filtered at {freqmin:.2f}-{freqmax:.2f}Hz')
        ax[0].set_xlabel('time [s]')
        ax[0].set_ylabel('waveforms')
        ax[0].set_xticks(t)
        ax[0].set_yticks(np.arange(0, nwin, step=int(nwin / 10)))
        ax[0].set_yticklabels(timestamp[0:nwin:int(nwin / 10)])
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

    if savefig:
        if sdir is None:
            sdir = os.path.join(DATADIR, 'plots')
        if not os.path.isdir(sdir):
            os.makedirs(sdir)
        outfname = os.path.join(sdir, f'{sfile.split("/")[-1].split(".")[0]}_{freqmin:.2f}_{freqmax:.2f}Hz.pdf')
        fig.savefig(outfname, format='pdf', dpi=300)
        print(f'Saving figure in {outfname}')
        plt.close(fig)
    else:
        plt.show()

# Loop over files to check them out
sfiles = glob.glob(os.path.join(DATADIR, '*', '*.h5'))
sfiles.sort()
for sfile in sfiles:
    print(f"Processing this file: {sfile}")
    try:
        plot_substack_all(sfile=sfile, freqmin=freqmin, freqmax=freqmax, ccomp=ccomp, disp_lag=50, savefig=True, sdir=sdir)
    except Exception as e:
        print(f"Skipping {sfile} due to an error: {e}")
        continue

