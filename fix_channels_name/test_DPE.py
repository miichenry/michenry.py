import os
from obspy import read

# Function to read filenames from a text file
def read_filenames_from_txt(txt_file):
    """
    Reads a list of filenames from a text file.
    Each line in the text file should contain a filename.
    """
    try:
        with open(txt_file, 'r') as file:
            filenames = file.read().splitlines()
        return filenames
    except Exception as e:
        print(f"Error reading the text file {txt_file}: {e}")
        return []

# Function to test if all channel names have been changed successfully
def test_channel_names(filenames, directory, expected_channel):
    success = True
    total_files = 0
    total_traces = 0
    failed_files = []

    # Iterate over the provided filenames
    for file_name in filenames:
        # Ensure the filename ends with "E.miniseed" and exists in the directory
        if file_name.endswith("E.miniseed"):
            file_path = os.path.join(directory, file_name)
            if os.path.exists(file_path):
                total_files += 1
                
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
            else:
                print(f"File {file_name} does not exist in the directory {directory}")
                failed_files.append(file_name)
    
    # Final report
    if success:
        print(f"All {total_files} files and {total_traces} traces have the correct channel name '{expected_channel}'")
    else:
        print(f"{len(failed_files)} files failed to update the channel names correctly.")
        print("Failed files:", failed_files)

# Main function to tie everything together
def main():
    txt_file = "/srv/beegfs/scratch/shares/cdff/DPM/mika_scripts/fix_channels_name/missing_files.txt"  # Replace with the path to your text file
    directory = "/srv/beegfs/scratch/shares/cdff/DPM/miniseed3"  # Replace with the directory where MiniSEED files are stored
    expected_channel_name = "DPE"  # The expected channel name
    
    # Read filenames from the text file
    filenames = read_filenames_from_txt(txt_file)
    
    if filenames:
        # Run the test for channel names
        test_channel_names(filenames, directory, expected_channel_name)
    else:
        print("No filenames to process.")

if __name__ == "__main__":
    main()
