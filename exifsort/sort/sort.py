#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""exif sort implementation"""

# BSD 2-Clause License
#
# Copyright (c) 2019, Yasuhiro Okuno (Koma)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import platform
import re
import shutil
import time
from datetime import date
from enum import IntEnum

import click
from PIL import Image
from PIL.ExifTags import TAGS


class Level(IntEnum):
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

def pout(msg=None, Verbose=False, level=Level.INFO, newline=True):
    """stdout support method
    :param msg: message to print
    :param Verbose: Set True to print DEBUG message
    :param level: Set message level for coloring
    """
    error=False
    if level in {Level.NOTSET, Level.DEBUG}:
        # blah
        if not Verbose:
            return
        fg = 'magenta'
    elif level == Level.INFO:
        fg = 'green'
    elif level == Level.WARNING:
        fg = 'yellow'
        error=True
    elif level in {Level.ERROR, Level.CRITICAL}:
        fg = 'red'
        error=True
    else:
        pass
    click.echo(click.style(str(msg), fg=fg), nl=newline, err=error)

def copyImage(src, dst, dryrun=False, overwrite=False, verbose=False):
    """copy image from src to dst
    :param src: path to image to copy
    :param dst: directory path to copy src to
    :param dryrun: dryrun if set to True
    :param verbose: set to true to output debug messages
    """
    pout("{img} => {toDir}".format(img=os.path.abspath(src), toDir=os.path.abspath(dst)), verbose, Level.INFO)
    if not dryrun:
        if os.path.exists(dst):
            if overwrite:
                # delete file and copy
                try:
                    os.remove(dst)
                except:
                    pout("could not overwrite {file}".format(file=dst))
                    return
            else:
                pout("{file} already exists.".format(file=dst), verbose, Level.WARNING)
                return
        try:
            os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
            shutil.copy2(os.path.abspath(src), os.path.abspath(dst))
        except:
            pout("could not copy to {file}".format(file=os.path.abspath(dst)), verbose, Level.WARNING)
    else:
        pout("DRY RUN... nothing is copied", verbose, Level.INFO)

def moveImage(src, dst, dryrun=False, overwrite=False, verbose=False):
    """move image from src to dst
    :param src: path to image to move
    :param dst: directory path to move src to
    :param dryrun: dryrun if set to True
    :param verbose: set to true to output debug messages
    """
    pout("{img} => {toDir}".format(img=os.path.abspath(src), toDir=os.path.abspath(dst)), verbose, Level.INFO)
    if not dryrun:
        if os.path.exists(dst):
            if overwrite:
                # delete file and copy
                try:
                    os.remove(dst)
                except:
                    pout("could not overwrite {file}".format(file=dst))
                    return
            else:
                pout("{file} already exists.".format(file=dst), verbose, Level.WARNING)
                return
        try:
            os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
            shutil.move(os.path.abspath(src), os.path.abspath(dst))
        except:
            pout("could not move to {dst}".format(dst=os.path.abspath(dst)), verbose, Level.WARNING)
    else:
        pout("DRY RUN... nothing is moved", verbose, Level.INFO)

def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return date(*time.localtime(os.path.getctime(path_to_file))[:3])
    else:
        stat = os.stat(path_to_file)
        try:
            return date(*time.localtime(stat.st_birthtime)[:3])
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return date(*time.localtime(stat.st_mtime)[:3])

def getDateOfImage(fpath, verbose=False):
    rt = None
    # First try to get date from exif
    try:
        img = Image.open(fpath)
        exif = img._getexif()
        try:
            for id,val in exif.items():
                tg = TAGS.get(id,id)
                if tg == "DateTimeOriginal":
                    dtArr = re.split('[ :]', val)
                    rt = date(int(dtArr[0]), int(dtArr[1]), int(dtArr[2]))
            img.close()
        except AttributeError:
            pout("Exif not found: {filename}".format(filename=fpath),
                verbose,
                Level.DEBUG)
    except:
        pout("{filename} not an image".format(filename=fpath),
            verbose,
            Level.DEBUG)
    if rt == None:
        rt = creation_date(fpath) # still needed to support .mov and other files
    return rt

def getImages(flist=[], verbose=False):
    for fpath in flist:
        dateinfo = getDateOfImage(fpath, verbose)
        # if datetimeinfor is "NON", get the date from os
        yield ({"path": fpath, "date" : dateinfo})

def getTgtDir(basePath, fmt, filedate, filename, hierarch=False, verbose=False, makedir=False):
    """generate the path to move file to based on base path and format.
    If the path does not exist, the directories will be generated as well.
    :param basePath: path where directories are made
    :param fmt: formatting for the directory path
    :param filedate: datetime.date object.  path will be based on this date
    :param hierarch: ignore fmt and create a new hierarchical path %Y/%m/%d
    :param verbose: verbose mode if set to True
    :param makedir: create the target path if True
    returns a string
    """
    rt = None
    if not hierarch:
        rt = os.path.join(basePath, filedate.strftime(fmt))
    else:
        rt = os.path.join(basePath, filedate.strftime(r"%Y"), filedate.strftime(r"%m"), filedate.strftime(r"%d"))
    if makedir:
        os.makedirs(rt, exist_ok=True)
    return os.path.join(rt, filename)

def sort(kwargs, func):
    """Sort images to sorted directories using func
    :param kwargs: argument dictionary created by click
    :func: function to use to transfer the file
    """
    # 'srcdir': source directory to search (string)
    sSrc = kwargs['srcdir']
    # 'tgtdir': target directory to move/copy to (string)
    sTgt = kwargs['tgtdir']
    # 'recurse': recursively search inside srcdir (bool)
    bRec = kwargs['recurse']
    # 'overwrite': overwrite target (bool)
    bOverwrite = kwargs['overwrite']
    # 'hierarch': create hierarchical subdirectory structure in tgtdir (bool)
    bHier = kwargs['hierarch']
    # 'fmt': date format to use as subdirectory name in tgtdir (string)
    sFmt = kwargs['fmt']
    # 'verbose': verbose mode flag (bool)
    bVerb = kwargs['verbose']
    # 'dry-run':
    bDry = kwargs['dry_run']
    # Step 1:
    # search for images in kwargs["srcdir"]
    # TODO: prune file list of non-image files based on file extensions
    # jpg, jpeg, png, gif, tiff, tif, bmp, webp, img
    flist = []
    if bRec:
        for subdir, _, files in os.walk(sSrc):
            for fpath in files:
                flist.append(subdir + os.sep + fpath)
    else:
        for fpath in os.listdir(sSrc):
            flist.append(fpath)
    pout(flist, bVerb, Level.DEBUG)
    extensions = ( '.jpg', '.jpeg', '.png', '.gif', '.tif', '.tiff', '.bmp', '.webp', '.img', '.mov', '.mp4', '.3gp', '.avi')
    flist = [ file for file in flist if file.lower().endswith(extensions) ]
    # Step 2:
    # Move/Copy files to kwargs["dstdir"]/<formatted date dir>
    i = 0
    num = len(flist)
    for image in getImages(flist, bVerb):
        pout(image, bVerb, Level.DEBUG)
        i += 1
        pout("{current}/{total} : ".format(
            current=i,
            total=num),
            bVerb, Level.INFO, newline=False)
        func(image["path"],
            getTgtDir(
                sTgt,
                sFmt,
                image["date"],
                os.path.basename(image["path"]),
                bHier,
                bVerb),
            bDry,
            bOverwrite,
            bVerb)
        # use func(src, dst, verbose) to move/copy image to appropriate path
    return

def cp(kwargs):
    """Copy images to sorted directories."""
    pout(kwargs, kwargs["verbose"], Level.DEBUG)
    sort(kwargs, copyImage)
    pass

def mv(kwargs):
    """Move images to sorted directories."""
    pout(kwargs, kwargs["verbose"], Level.DEBUG)
    sort(kwargs, moveImage)
    pass
