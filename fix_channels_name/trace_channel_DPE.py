import os
from obspy import read
from obspy.core import UTCDateTime

# Define the directory where your MiniSEED files are stored
input_directory = "/srv/beegfs/scratch/shares/cdff/DPM/missing_files"
output_directory = "/srv/beegfs/scratch/shares/cdff/DPM/miniseed_corrected"  # Directory to save modified files

# Function to update trace.stats
def modify_trace_stats(trace):
    # Modify trace.stats attributes (example modifications)
    #trace.stats.network = "XX"
    #trace.stats.station = "TEST"
    #trace.stats.location = ""
    trace.stats.channel = "DPE"
    #trace.stats.starttime = UTCDateTime(2020, 1, 1)  # Set start time to Jan 1, 2020
    return trace

# Create output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Iterate over all MiniSEED files in the directory
for file_name in os.listdir(input_directory):
    if file_name.endswith("E.miniseed"):
        file_path = os.path.join(input_directory, file_name)
        
        # Read the MiniSEED file
        st = read(file_path)
        print("Channel in loaded st:", st[0].stats.channel) 
        # Modify the stats for each trace in the Stream object
        for trace in st:
            trace = modify_trace_stats(trace)
        
        # Save the modified traces to a new file in the output directory
        output_file_path = os.path.join(output_directory, file_name)
        st.write(output_file_path, format="MSEED")
        print(f"Modified and saved: {output_file_path}")

print("Processing complete.")
