import os

# Specify the directory containing the files
directory = '/srv/beegfs/scratch/shares/cdff/DPM/miniseed2'

# List all files in the directory
files = os.listdir(directory)

# Iterate over each file
for filename in files:
    # Skip directories
    if os.path.isdir(os.path.join(directory, filename)):
        continue
    
    # Construct the new filename
    new_filename = 'SS' + filename[2:]
    
    # Get the full paths
    old_file = os.path.join(directory, filename)
    new_file = os.path.join(directory, new_filename)
    
    # Rename the file
    os.rename(old_file, new_file)
    print(f'Renamed: {filename} -> {new_filename}')
