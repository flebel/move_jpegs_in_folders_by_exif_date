#!/usr/bin/env python

#   Copyright (C) 2011 Francois Lebel <francoislebel@gmail.com>
#   http://github.com/flebel/move_jpegs_in_folders_by_exif_date
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#   move_jpegs_in_folders_by_exif_date
#   A script to move JPEG files in directories ('yyyy-mm-dd') according
#   to their Exif.Image.DateTime EXIF tag. The directory given as the
#   positional argument is not searched recursively and will become the
#   parent directory for the created directories.
#
#   Dependencies:
#     pyexiv2 0.2.2 http://tilloy.net/dev/pyexiv2/

from optparse import OptionParser
import glob
import os
import pyexiv2
import shutil

EXIF_DATE_KEY = 'Exif.Image.DateTime'
JPEG_EXTENSIONS = ('JPG', 'JPEG')

def main():
    parser = OptionParser(usage='Usage: %prog path_to_directory')
    parser.add_option('--dry-run', action='store_true', default=False, dest='dry_run', help='display the actions that will be undertaken without actually executing them')
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("the files' directory must be supplied as the only positional argument.")
    directory = args[0]
    if not os.path.isdir(directory):
        parser.error("the files' directory specified is invalid.")
    # Get the absolute path and normalize its case
    directory = os.path.realpath(os.path.normcase(directory))
    run(directory, options.dry_run)

def run(directory, dry_run):
    files = []
    for extension in JPEG_EXTENSIONS:
        file_glob = "%s*.%s" % (os.path.join(directory, '*'), extension)
        files.extend(glob.glob(file_glob))
    files.sort()
    for f in files:
        # Read EXIF metadata and extract the date the photo was taken
        metadata = pyexiv2.ImageMetadata(f)
        metadata.read()
        if EXIF_DATE_KEY not in metadata.exif_keys:
            continue
        date = metadata[EXIF_DATE_KEY].value
        date_directory_name = "%d-%d-%d" % (date.year, date.month, date.day)
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
        moving_msg = "Moving file '%s' into '%s'..." % (file_name, date_directory_path)
        if not dry_run:
            print moving_msg,
            shutil.move(f, moved_file_path)
        else:
            print '[dry-run]', moving_msg,
        print 'Done.'

if __name__ == "__main__":
    main()

