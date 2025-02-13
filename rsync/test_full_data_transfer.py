""" Reads the stations column out a .csv and check if this stations has a mseed in a directory.
Call:
python test....py

- csv_file_path
- directory_path

"""
import os
import pandas as pd

# Path to the CSV file and the directory to check
csv_file_path = '/srv/beegfs/scratch/shares/cdff/DPM/NANT/coordinates_smartsolo2.csv'
directory_path = '/srv/beegfs/scratch/shares/cdff/DPM/miniseed3'
output_file_path = '/srv/beegfs/scratch/shares/cdff/DPM/mika_scripts/rsync/stations_not_found.txt'

# Read the CSV file
stations_df = pd.read_csv(csv_file_path)

# Get the list of stations from the 'station' column
stations = stations_df['station'].tolist()

stations_not_found = []

# Iterate through the directory and check for files corresponding to each station
for station in stations:
    station_files = [entry.name for entry in os.scandir(directory_path) if entry.is_file() and str(station) in entry.name]
    if not station_files:
        stations_not_found.append(station)
        print(f"No files found for station {station}")

# Save stations_not_found to a text file
with open(output_file_path, 'w') as f:
    for station in stations_not_found:
        f.write(f"{station}\n")
        
