import os
import shutil

# Define source and target directories
SOURCE_DIR = "/srv/beegfs/scratch/shares/cdff/DPM/miniseed3"  # Replace with your source directory path
TARGET_DIR = "/srv/beegfs/scratch/shares/cdff/DPM/missing_files"  # Replace with your target directory path

# Path to the missing files list
MISSING_FILES_PATH = "missing_files.txt"

# Check if missing_files.txt exists
if not os.path.isfile(MISSING_FILES_PATH):
    print("Error: missing_files.txt not found!")
    exit(1)

# Ensure the target directory exists
if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)

# Read filenames from missing_files.txt and copy them
with open(MISSING_FILES_PATH, 'r') as file_list:
    for filename in file_list:
        filename = filename.strip()  # Remove any leading/trailing whitespace
        if filename:
            source_file = os.path.join(SOURCE_DIR, filename)
            target_file = os.path.join(TARGET_DIR, filename)
            
            if os.path.isfile(source_file):
                # Copy file to target directory
                shutil.copy(source_file, target_file)
                print(f"Copied: {filename}")
            else:
                print(f"Warning: {filename} not found in source directory.")

print("File copy process completed.")
