import os
import pandas as pd

# Load the CSV file into a DataFrame
csv_file_path = '/srv/beegfs/scratch/shares/cdff/DPM/NANT/station_2_SN.csv'
df = pd.read_csv(csv_file_path, converters={'SN': str})

# Create a dictionary for quick lookup
station_to_sn = dict(zip(df['station'].astype(str), df['SN']))

# Directory containing the files to rename
directory_path = '/srv/beegfs/scratch/shares/cdff/DPM/miniseed2'

# Function to rename files
def rename_files_in_directory(directory):
    for filename in os.listdir(directory):
        # Check if the filename contains the pattern with number between "." and ".."
        if '.' in filename and '..' in filename:
            try:
                # Extract the number between "." and ".."
                number = filename.split('.')[1].split('..')[0]
                
                # Get the corresponding SN value from the dictionary
                new_value = station_to_sn.get(number, None)
                
                if new_value:
                    # Create the new filename
                    new_filename = filename.replace(f'.{number}..', f'.{new_value}..')
                    
                    # Construct the full old and new file paths
                    old_file_path = os.path.join(directory, filename)
                    new_file_path = os.path.join(directory, new_filename)
                    
                    # Rename the file
                    os.rename(old_file_path, new_file_path)
                    print(f'Renamed: {filename} -> {new_filename}')
                else:
                    print(f'No SN value found for station: {number}')
            except Exception as e:
                print(f'Error processing file {filename}: {e}')

# Run the renaming function
rename_files_in_directory(directory_path)
