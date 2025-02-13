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
config_file = sys.argv[1]
with open(config_file, 'r') as file:
    para = yaml.safe_load(file)

print("Loaded Configuration:")
print(para)

# data/file paths
title   = para['title']       # Plot title (para. for subsequent function)
DATADIR = para['DATADIR']   # dir with data in ASDF format
figname = para['figname']   # figure name (para. for subsequent function)
OUTDIR  = para['OUTDIR']    # Path where to save figure (para. for subsequent function)

def plot_availability(wdir, title, plot=False, savefig=False, figname=None):
    """
    Make a bar plot of data availability based on folder with H5 files for raw data created with S0B script
    Args:
        wdir: Path to the H5 files created with script S0B [str]
        title: Plot title [str]
        plot: Whether to make the plot or not [bool]
        savefig: Whether to save the figure or not [bool]
        figname: Path where to save figure [str]

    Returns:
        Pandas.DataFrame with data availability for each station

    """

    # Get files
    sfiles = glob.glob(os.path.join(wdir, "*.h5"))
    sfiles.sort()

    # Extract availability and Build dataframe
    dfa = []
    for _i, sf in enumerate(sfiles):
        print(f"Processing file {_i+1}/{len(sfiles)}: {sf}")
        if _i % 20 == 0: print(f"Reading files {_i+1}/{len(sfiles)}...")
        t1 = os.path.split(sf)[1].split("T")[0].strip("_")
        t2 = os.path.split(sf)[1].split("T")[1].strip("_").strip(".h5")
        st1 = obspy.UTCDateTime(t1)
        st2 = obspy.UTCDateTime(t2)

        try:
            with pyasdf.ASDFDataSet(sf, mode="r") as ds:
                stalst = ds.waveforms.list()
                print(f"Number of stations: {len(stalst)}")
                for sta in stalst:
                    num = len(ds.waveforms[sta].list())
                    print(f"Station: {sta}, Number of components: {num}")
                    dum = pd.DataFrame(data={"Station": [sta],
                                         "Start": [st1._get_datetime()],
                                         "End": [st2._get_datetime()],
                                              "num_comps": [num]
                                        }, index=None)
                    dfa.append(dum)
        except Exception as e:
            print(f"Error processing file {sf}: {e}")
    dfa = pd.concat(dfa, axis=0)

    if plot:
        station, start, stop, num_comps = dfa["Station"], dfa["Start"], dfa["End"], dfa["num_comps"]

        # Unique stations
        stalst, unique_idx, stalst_inv = np.unique(station, 1, 1)
        #print(stalst)

        #Build y values from the number of unique stations
        y = (stalst_inv + 1) / float(len(stalst) + 1)

        # Create fig handles
        fig, ax = plt.subplots(1,1,figsize=(14,0.5*len(stalst)))

        # Plot availability
        for b, nc, start1, stop1 in zip(y, num_comps, start, stop):
            if nc < 4:
                ax.hlines(b, start1, stop1, color="r", lw=8)
            elif nc == 4:
                ax.hlines(b, start1, stop1, color="g", lw=8)
            else:
                ax.hlines(b, start1, stop1, color="b", lw=8)
        # X axis
        ax.xaxis_date()
        myFmt = DateFormatter('%Y-%m-%d')
        ax.xaxis.set_major_formatter(myFmt)

        delta = (stop.max() - start.min())/20
        num_xticks = 20

        minterval = max((int(np.floor((stop.max() - start.min()).days / num_xticks))//7)*7,1)

        if int(np.floor((stop.max() - start.min()).days/num_xticks)) > 30:
            minterval = minterval // 30
            ax.xaxis.set_major_locator(MonthLocator(interval=minterval)) # used to be SecondLocator(0, interval=20)
        else:
            ax.xaxis.set_major_locator(DayLocator(interval=minterval)) # used to be SecondLocator(0, interval=20)
        if int(np.floor((stop.max() - start.min()).days/num_xticks)) > 30:
            sinterval = 1
            ax.xaxis.set_minor_locator(MonthLocator(interval=sinterval))
        else:
            sinterval = 7
            ax.xaxis.set_minor_locator(DayLocator(interval=sinterval))
        plt.xticks(rotation=90)
        ax.set_xlim(start.min()-delta, stop.max()+delta)
        # ax.set_xlabel('Time')
        ax.tick_params(which='major', length=7, width=2)

        # Y axis
        plt.yticks(y[unique_idx], stalst)
        ax.set_ylim(0,1)

        # Title
        ax.set_title(title)

        # Grid
        plt.grid(b=True, which='both', color='0.65', linestyle='-')
        # plt.grid(b=True, which='minor', color='0.65', linestyle='-')

        # Save or show
        if savefig and figname:
            plt.savefig(figname, format="PNG", dpi=300)
            print("Figure saved as {figname}")
        else:
            plt.show()
        plt.close()

    return dfa

figpath = os.path.join(OUTDIR, figname)
plot_availability(wdir=DATADIR, title=title, plot=True, savefig=True, figname=figpath)
