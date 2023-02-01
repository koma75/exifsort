exifsort
========================================================================

**TOOL CONSOLIDATED TO https://github.com/koma75/imgtk**

Command line tool to sort image files in one folder to another by date
of image (exif meta-data or file creation date).

Installation
------------------------------------------------------------------------

~~~shell
> pip install exifsort
~~~

Usage
------------------------------------------------------------------------

### Move command

~~~text
Usage: exifsort mv [OPTIONS] SRCDIR TGTDIR

  Sort and Move images from SRCDIR to TGTDIR.

Options:
  -r, --recurse    Search for images in SRCDIR recursively
  -o, --overwrite  Overwrite files in TGTDIR
  -H, --hierarch   Create a hierarchical directory for Year, Month and Date in
                   TGTDIR
  -d, --dry-run    Dry run the command without moving
  -f, --fmt <fmt>  Format target directory name using date format string give
                   in <fmt>.  Use Python strftime directives.
  -V, --verbose    output in verbose mode
  -h, --help       Show this message and exit.
~~~

Moves the images inside SRCDIR into sorted folders under TGTDIR.
Target folders will be sorted based on the date the image was created
(Referes to Exif meta-data or the file creation date if exif is not
available).

#### Options

* -r, --recursive
    * search images in SOURCEDIR and any subdirectories.
* -o, --overwrite
    * overwrite any image files in TARGETDIR
* -H, --hierarch
    * create a folder for year, month and date in a hierarchical manner
      instead of one folder for each date.
* -d, --dry-run
    * dry run the command.  nothing will be moved
* -f, --fmt DATEFORMAT
    * format the folder name using date format string specified by DATEFORMAT
    * ignored when "-h" is specified.
* -v, --verbose
    * verbose mode

### Copy command

~~~shell
> exifsort cp [OPTIONS] SOURCEDIR TARGETDIR
~~~

same options as move, but copies all source files to destination instead
of moving the files.
