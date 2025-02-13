import os

# Directory containing the files
directory = '/srv/beegfs/scratch/shares/cdff/DPM/miniseed'

# Loop through all files in the directory
for filename in os.listdir(directory):
    # Check if the file ends with .E.miniseed and contains DPZ
    if filename.endswith('.E.miniseed') and 'DPZ' in filename:
        # Create the new filename
        new_filename = filename.replace('DPZ', 'DPE')
        # Get full file paths
        old_file = os.path.join(directory, filename)
        new_file = os.path.join(directory, new_filename)
        # Rename the file
        os.rename(old_file, new_file)
        print(f'Renamed: {filename} -> {new_filename}')
