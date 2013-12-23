#!/usr/bin/env python

from optparse import OptionParser
import glob
import os
import pyexiv2
import shutil

EXIF_DATE_KEY = 'Exif.Image.DateTime'
# Look for files with a 'JPG' or 'JPEG' extension (case insensitive.)
# Note that glob does not support regular expressions, hence the duplication.
JPEG_EXTENSIONS = ('[jJ][pP][gG]', '[jJ][pP][eE][gG]')

def main():
    parser = OptionParser(usage='Usage: %prog [OPTIONS] PATH')
    parser.add_option('--move-twin-files', action='store_true', default=True, dest='move_twin_files', help="also move the files that are prefixed by the JPEG's filename without its extension, ie. IMG_0001.JPG and IMG_0001.CR2")
    parser.add_option('--dry-run', action='store_true', default=False, dest='dry_run', help='display the actions that will be undertaken without actually executing them')
    (options, args) = parser.parse_args()
    # Use the current directory if none has been specified
    if len(args) != 1:
        directory = os.getcwdu()
    else:
        directory = args[0]
    if not os.path.isdir(directory):
        parser.error("the files' directory specified is invalid.")
    # Get the absolute path and normalize its case
    directory = os.path.realpath(os.path.normcase(directory))
    run(directory, options.move_twin_files, options.dry_run)

def run(directory, move_twin_files, dry_run):
    files = []
    for extension in JPEG_EXTENSIONS:
        file_glob = "%s.%s" % (os.path.join(directory, '*'), extension)
        files.extend(glob.glob(file_glob))
    files.sort()
    for f in files:
        # Read EXIF metadata and extract the date the photo was taken
        metadata = pyexiv2.ImageMetadata(f)
        metadata.read()
        if EXIF_DATE_KEY not in metadata.exif_keys:
            continue
        date = metadata[EXIF_DATE_KEY].value
        date_directory_name = "%d-%02d-%02d" % (date.year, date.month, date.day)
        # Create the directory
        date_directory_path = os.path.join(directory, date_directory_name)
        if not os.path.exists(date_directory_path):
            directory_msg = "Creating directory '%s'..." % date_directory_path
            if not dry_run:
                print directory_msg,
                os.mkdir(date_directory_path)
            else:
                print '[dry-run]', directory_msg,
            print 'Done.'
        file_name = os.path.basename(os.path.join(date_directory_path, f))
        moved_file_path = os.path.join(date_directory_path, file_name)
        # Move the photo into the directory
        moving_msg = '%s -> %s ...' % (file_name, moved_file_path)
        if not dry_run:
            print moving_msg,
            shutil.move(f, moved_file_path)
        else:
            print '[dry-run]', moving_msg,
        print 'Done.'
        # Move the files that are prefixed by the filename without its
        # extension, ie. IMG_0001.JPG and IMG_0001.CR2
        if move_twin_files:
            basename = os.path.splitext(f)[0]
            twin_files_glob = "%s.*" % basename
            twin_files = glob.glob(twin_files_glob)
            # Remove the current file from the list if it hasn't been moved
            # as no action is being executed
            if dry_run:
                twin_files.remove(f)
            for tf in twin_files:
                twin_file_name = os.path.basename(os.path.join(date_directory_path, tf))
                twin_moved_file_path = os.path.join(date_directory_path, twin_file_name)
                twin_moving_msg = '%s -> %s ...' % (twin_file_name, twin_moved_file_path)
                if not dry_run:
                    print twin_moving_msg,
                    shutil.move(tf, twin_moved_file_path)
                else:
                    print '[dry-run]', twin_moving_msg,
                print 'Done.'

if __name__ == "__main__":
    main()

