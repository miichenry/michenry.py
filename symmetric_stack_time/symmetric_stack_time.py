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
import time
sys.path.insert(0, '/srv/beegfs/scratch/shares/cdff/DPM/NANT/NoisePy-ant-main/noisepy')
from filter import lowpass
from obspy.signal.filter import bandpass
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, DayLocator, MonthLocator
from scipy.fftpack import next_fast_len, fft, ifft
import scipy.fftpack as sfft
from matplotlib.ticker import MultipleLocator
from numpy import matlib as mb
import pandas as pd
from obspy import Trace, Stream

# PARAMETER SECTION
config_file = sys.argv[1]
with open(config_file, 'r') as file:
    para = yaml.safe_load(file)

print("Loaded Configuration:")
print(para)

# data/file paths
DATADIR = para['DATADIR']   # dir with data in ASDF format
figname = para['figname']   # figure name (para. for subsequent function)
OUTDIR  = para['OUTDIR']    # Path where to save figure (para. for subsequent function)
freqmin = para['freqmin']
freqmax = para['freqmax']

def get_stack_gather(sfiles, stack_method="Allstack_nroot", comp="ZZ"):
    """
    This function takes in a list of the H5 stack files and outputs the CCFs and key information into numpy arrays,
    for further analysis (e.g. bin stacks, beamforming, FK analysis)
    Args:
        sfiles: List of stack files in H5 format outputted by NoisePy. One file per station pair.
        stack_method: Stack method to use as labelled in the H5 files (e.g. "Allstack_linear")
        comp: Cross-component to extract (e.g. "ZZ", "TT", ...)

    Returns:
        ncfs0: 2D array of FFT of CCFs. Dimensions: (station pairs, frequencies)
        r0: Vector of inter-station distances, in the same order as first dimension of ncfs0 [km]
        f: Vector of frequencies, in the same order as second dimension of ncfs0
        ncts0: 2D array of CCFs in time domain. Dimensions: (station pairs, time lag)
        t: Vector of time lags, corresponding to 2nd dimension of ncts0
        dt: Sampling time interval (1 / sampling rate)
        azimuth: Azimuth from source station to receiver station
        numgood: Number of individual raw CCFs used in the stack

    """
    # Get parameters
    nPairs = len(sfiles)
    with pyasdf.ASDFDataSet(sfiles[0], mode="r") as ds:
        dt = ds.auxiliary_data[stack_method][comp].parameters["dt"]  # 0.04
        n = np.array(ds.auxiliary_data[stack_method][comp].data).shape[0]  # 3001 for 60 s lag, dt = 0.04
    Nfft = int(next_fast_len(n))  # 3072

    # Necessary variables for CC-FJpy: r, f, ncfs
    ncfs = np.zeros([nPairs, Nfft], dtype=np.complex64)  # array of CCFs in spectral domain
    r = np.zeros(nPairs)  # array of distances between pairs
    t = np.arange(-((n - 1) / 2) * dt, ((n) / 2) * dt, dt)  # Array of lag time
    ncts = np.zeros([nPairs, n], dtype=np.float32)  # Array of CCFs in time domain
    azimuth = np.zeros(nPairs)
    numgood = np.zeros(nPairs)

    # Get ncfs
    t0 = time.time()  # To get runtime of code
    ibad = []  # Indices for corrupted data files
    for _i, filename in enumerate(sfiles):

        if _i % 1000 == 0: print(f"{_i + 1}/{nPairs}")

        # *** Read data from .h5
        try:
            with pyasdf.ASDFDataSet(filename, mode="r") as ds:
                dist = ds.auxiliary_data[stack_method][comp].parameters["dist"]
                ngood = ds.auxiliary_data[stack_method][comp].parameters["ngood"]
                tdata = np.array(ds.auxiliary_data[stack_method][comp].data)
                lonR = ds.auxiliary_data[stack_method][comp].parameters["lonR"]
                lonS = ds.auxiliary_data[stack_method][comp].parameters["lonS"]
                if lonS > lonR:  # Flip so we have West to East for positive lags
                    tdata = np.flip(tdata)
                    azi = ds.auxiliary_data[stack_method][comp].parameters["baz"]
                else:
                    azi = ds.auxiliary_data[stack_method][comp].parameters["azi"]
        except:
            ibad.append(_i)
            continue

        # *** fft
        data_fft = fft(tdata, Nfft, axis=0)  # [:Nfft//2]
        f = scipy.fftpack.fftfreq(Nfft, d=dt)  # Frequencies

        # *** Save distance and spectrum
        r[_i] = dist
        spec = ncfs[_i, :] + data_fft
        spec /= np.max(np.abs(spec))
        ncfs[_i, :] = spec
        numgood[_i] = ngood
        azimuth[_i] = azi

        # *** Save time domain CCF
        ncts[_i, :] = tdata

    print(f"Time elapsed to read data: {time.time() - t0:.0f}")

    # *** Remove bad indices
    ncfs = np.delete(ncfs, ibad, axis=0)
    ncts = np.delete(ncts, ibad, axis=0)
    r = np.delete(r, ibad, axis=0)

    # *** Sort by increasing distance
    indx = np.argsort(r)
    r0 = r[indx]
    ncfs0 = ncfs[indx, :]
    ncts0 = ncts[indx, :]

    return ncfs0, r0, f, ncts0, t, dt, azimuth, numgood


def symmetric_stack_time(ncts, t, r, dt, figpath, freqmin, freqmax, plot=True, tmaxplot=20):
    """
    Calculate the symmetric CCFs in the time domain as a function of inter-station distance and plot.
    Args:
        ncts: 2D array of CCFs in time domain, dimensions = (station pairs, time lag)
        t: Vector of time lag
        r: Vector of inter-station distances [km]
        plot: Whether to plot or not [bool]
        tmaxplot: Maximum time lag for plotting
        figpath: figure path for output

    Returns:
        Mp: Normalized 2D array of CCFs
        Mpsym: Normallized and symmetric 2D array of CCFs

    """
    df = int(1/dt)
    print(type(ncts))
    ncts = bandpass(ncts, freqmin, freqmax, df, corners=4, zerophase=True)
    M = ncts.copy()
    trace_num = np.arange(0, len(r))
    Mp = M / np.max(np.abs(M), axis=1, keepdims=True)  # Normalize by max
    # stack positive and negative lags
    imid = len(t) // 2
    Msym = M[:, imid:].copy()
    Msym[:, 1:] += np.flip(M[:, :imid].copy(), axis=1)
    Msym /= 2
    Msym /= np.max(np.abs(Msym), axis=1, keepdims=True)  # Normalize by max

    if plot:
        fig, ax = plt.subplots(1, 2, figsize=(12, 6))
        ax[0].pcolormesh(t, trace_num, Mp, cmap='gray', vmin=-1, vmax=1, shading="auto")
        ax[0].set_title("Causal and acausal")
        ax[0].set_ylabel('trace #')
        ax[0].set_xlabel('Time (s)')
        ax[0].set_xlim((-tmaxplot, tmaxplot))

        ax[1].pcolormesh(t[imid:], trace_num, Msym, cmap='gray', vmin=-1, vmax=1, shading="auto")
        ax[1].set_title("Symmetric CCF")
        ax[1].set_ylabel('trace #')
        ax[1].set_xlabel('Time (s)')
        ax[1].set_xlim((0, tmaxplot))
    
        fig.savefig(figpath, format='png', dpi=300)
        plt.close()

    return Mp, Msym

sfiles = glob.glob(os.path.join(DATADIR, "*","*.h5"))
sfiles.sort()
if not sfiles:
    raise ValueError(f"No H5 files found in directory {DATADIR}")
figpath = os.path.join(OUTDIR, figname)
ncfs0, r, f, ncts, t, dt, azimuth, numgood = get_stack_gather(sfiles, stack_method="Allstack_linear", comp="ZZ")
print("starting figure plotting")
symmetric_stack_time(ncts, t, r, dt, figpath, freqmin, freqmax, plot=True, tmaxplot=20)
# Loop over files to check them out
#for fname in filelist:
#    print(f"Processing this file: {fname}")
#    try:
#        plot_availability(wdir=f"{fname}", title=title, plot=False, savefig=True, figname=figname)
#    except Exception as e:
#                print(f"Skipping {fname} due to an error: {e}")
#                continue
