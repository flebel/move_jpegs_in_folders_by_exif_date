==================================
move_jpegs_in_folders_by_exif_date
==================================

A script to move JPEG files in directories ('yyyy-mm-dd') according to their Exif.Image.DateTime EXIF tag. The directory given as the positional argument is not searched recursively and will become the parent directory for the created directories. The --move-twin-files option can be used to move non-JPEG files that have the same basename as the JPEG file but differs in extension, such as RAW files.

Dependencies
============

- pyexiv2 0.2.2 http://tilloy.net/dev/pyexiv2/

