"""
Script to extract and visualize trace statistics from MiniSEED files in a nodal array.

This script processes MiniSEED files, extracts relevant trace statistics such as 
start time, trace length, network, station, and channel, and stores them in a CSV file. 
It also provides visualizations of the data, including:
    1. Histogram of trace lengths.
    2. Scatter plot of start times vs. trace lengths.
    3. Bar plot of the number of traces per station.

Requirements:
    - obspy: for reading MiniSEED files.
    - pandas: for data handling.
    - matplotlib: for data visualization.

Author: [Your Name]
Date: [Date]

Usage:
    Modify the RAWDATA variable to point to the directory containing MiniSEED files.
    The script will process all files with the .miniseed extension in the specified directory.
"""

import glob
import obspy
import pandas as pd
import os
import matplotlib.pyplot as plt

# Path to the raw data
RAWDATA = '/srv/beegfs/scratch/shares/cdff/DPM/miniseed'

# Temporary and final CSV filenames
tmpfname = "trace_stats_temp.csv"
fname = "trace_stats.csv"

# Initialize lists to store trace information
filepaths = []
starttimes = []
lengths_seconds = []
networks = []
stations = []
channels = []

# Find all .miniseed files
flist = glob.glob(os.path.join(RAWDATA, "*.miniseed"))

# Loop through all files and extract trace statistics
with open(tmpfname,"w") as of:
    of.write("filepath,starttime,length_seconds\n")
    for ind, f in enumerate(flist):
        if ind % 100 == 0: print(f"{ind+1}/{len(flist)}")
        traces = obspy.read(f, headonly=True)
        tstart = min([tr.stats.starttime for tr in dum])
        tend = max([tr.stats.endtime for tr in dum])
        length_seconds = tend - tstart
         
        starttimes.append(tstart)
        lengths_seconds.append(length_seconds) 
        # Loop through all traces in the file
        for tr in traces:
            filepaths.append(f)
            networks.append(tr.stats.network)
            stations.append(tr.stats.station)
            channels.append(tr.stats.channel)
            
df = pd.DataFrame({
    'filepath': filepaths,
    'starttime': starttimes,
    'length_seconds': lengths_seconds,
    'network': networks,
    'station': stations,
    'channel': channels
})

# Save DataFrame to CSV
df.to_csv(tmpfname, index=False)
print(f"Finished writing trace statistics to {tmpfname}")

# --- Data Visualization Section ---

# 1. Plot histogram of trace lengths
plt.figure(figsize=(10, 6))
plt.hist(df['length_seconds'], bins=50, color='blue', alpha=0.7)
plt.title('Distribution of Trace Lengths')
plt.xlabel('Trace Length (seconds)')
plt.ylabel('Number of Traces')
plt.grid(True)
plt.savefig('trace_length_distribution.png')  # Save the histogram
plt.close()  # Close the plot after saving

# 2. Scatter plot of start times and trace lengths and save it
plt.figure(figsize=(10, 6))
plt.scatter(df['starttime'], df['length_seconds'], alpha=0.5, color='green')
plt.title('Trace Lengths over Time')
plt.xlabel('Start Time')
plt.ylabel('Trace Length (seconds)')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig('trace_lengths_over_time.png')  # Save the scatter plot
plt.close()

# 3. Bar plot of traces per station and save it
station_counts = df['station'].value_counts()
plt.figure(figsize=(12, 6))
station_counts.plot(kind='bar', color='purple')
plt.title('Number of Traces per Station')
plt.xlabel('Station')
plt.ylabel('Number of Traces')
plt.grid(True)
plt.tight_layout()
plt.savefig('traces_per_station.png')  # Save the bar plot
plt.close()
