import os

def get_filenames(directory, file_extension):
    """
    Returns a set of filenames (without the extension) for files in a directory that have the given extension.
    """
    filenames = set()
    for filename in os.listdir(directory):
        if filename.endswith(file_extension):
            filenames.add(filename)
    return filenames

def find_missing_files(dir1, dir2, file_extension):
    """
    Finds files in dir1 that are missing from dir2 based on filenames (with a specific extension).
    """
    dir1_files = get_filenames(dir1, file_extension)
    dir2_files = get_filenames(dir2, file_extension)

    missing_files = dir1_files - dir2_files  # Files in dir1 but not in dir2
    return missing_files

def main():
    dir2 = "/srv/beegfs/scratch/shares/cdff/DPM/miniseed_corrected"  # Replace with the actual path to directory1
    dir1 = "/srv/beegfs/scratch/shares/cdff/DPM/miniseed3"  # Replace with the actual path to directory2
    file_extension = "E.miniseed"

    missing_files = find_missing_files(dir1, dir2, file_extension)

    if missing_files:
        print("Missing files from directory2:")
        for missing_file in missing_files:
            print(missing_file)
    else:
        print("No missing files found.")

if __name__ == "__main__":
    main()
