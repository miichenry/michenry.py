import os
from obspy import read

# Define the directory where the modified MiniSEED files are stored
output_directory = "/srv/beegfs/scratch/shares/cdff/DPM/miniseed_corrected"

# The expected new channel name (as per the modify_trace_stats function)
expected_channel_name = "DPE"

# Function to test if all channel names have been changed successfully
def test_channel_names(directory, expected_channel):
    success = True
    total_files = 0
    total_traces = 0
    failed_files = []
    
    # Iterate over all MiniSEED files in the directory
    for file_name in os.listdir(directory):
        if file_name.endswith("E.miniseed"):
            total_files += 1
            file_path = os.path.join(directory, file_name)
            
            try:
                # Read the MiniSEED file
                st = read(file_path)
                
                # Check each trace in the stream
                for trace in st:
                    total_traces += 1
                    if trace.stats.channel != expected_channel:
                        print(f"Error in file {file_name}, trace {trace.id}: Channel is '{trace.stats.channel}' instead of '{expected_channel}'")
                        success = False
                        failed_files.append(file_name)
                        
            except Exception as e:
                print(f"Error reading file {file_name}: {e}")
                success = False
                failed_files.append(file_name)
    
    # Final report
    if success:
        print(f"All {total_files} files and {total_traces} traces have the correct channel name '{expected_channel}'")
    else:
        print(f"{len(failed_files)} files failed to update the channel names correctly.")
        print("Failed files:", failed_files)

# Run the test
test_channel_names(output_directory, expected_channel_name)
