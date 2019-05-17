exifsort
========================================================================

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

~~~shell
> exifsort mv [OPTIONS] SOURCEDIR TARGETDIR
~~~

Moves the images inside SOURCEDIR into sorted folders under TARGETDIR.
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
* -g, --geotag (Not Implemented)
    * create a folder for each country and state/province using Google
      Geotag API.
* -f, --fmt DATEFORMAT
    * format the folder name using date format string specified by DATEFORMAT
    * ignored when "-h" is specified.
* -v, --verbose

### Copy command

~~~shell
> exifsort cp [OPTIONS] SOURCEDIR TARGETDIR
~~~

same options as move, but copies all source files to destination instead
of moving the files.
