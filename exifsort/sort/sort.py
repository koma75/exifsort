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

def pout(msg=None, Verbose=False, level=Level.INFO):
    """stdout support method
    :param msg: message to print
    :param Verbose: Set True to print DEBUG message
    :param level: Set message level for coloring
    """
    if level in {Level.NOTSET, Level.DEBUG}:
        # blah
        if not Verbose:
            return
        fg = 'magenta'
    elif level == Level.INFO:
        fg = 'green'
    elif level == Level.WARNING:
        fg = 'yellow'
    elif level in {Level.ERROR, Level.CRITICAL}:
        fg = 'red'
    else:
        pass
    click.echo(click.style(str(msg), fg=fg))

def copyImage(src, dst, verbose=False):
    """copy image from src to dst
    :param src: path to image to copy
    :param dst: directory path to copy src to
    :param verbose: set to true to output debug messages
    """
    pass

def moveImage(src, dst, verbose=False):
    """move image from src to dst
    :param src: path to image to move
    :param dst: directory path to move src to
    :param verbose: set to true to output debug messages
    """
    pout("moving image", verbose, Level.DEBUG)
    pass

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
            pout("Exif read error: {filename}\n".format(filename=fpath),
                verbose,
                Level.DEBUG)
    except:
        pout("{filename} not an image\n".format(filename=fpath),
            verbose,
            Level.DEBUG)

    # If no exif in image, get data from os
    if rt == None:
        rt = creation_date(fpath)
        pass

    return rt

def getImages(flist=[], verbose=False):
    for fpath in flist:
        dateinfo = getDateOfImage(fpath, verbose)
        # if datetimeinfor is "NON", get the date from os
        # TODO: Should yield image path and target directory path
        yield ({fpath, dateinfo})

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

    # Step 1:
    # search for images in kwargs["srcdir"] and obtain date of image
    # and create destination path to move/copy to
    flist = []
    if bRec:
        for subdir, dirs, files in os.walk(sSrc):
            for fpath in files:
                flist.append(subdir + os.sep + fpath)
    else:
        for fpath in os.listdir(sSrc):
            flist.append(fpath)
    pout(flist, bVerb, Level.DEBUG)

    # Step 2:
    # Move/Copy files to kwargs["dstdir"]/<formatted date dir>
    with click.progressbar(getImages(flist, bVerb), label="Processing Images") as images:
        for image in images:
            pout(image, bVerb, Leve.DEBUG)
            // func(kwargs["srcdir"], kwargs["tgtdir"], kwargs)

def cp(kwargs):
    """Copy images to sorted directories."""
    pout("Not yet implemented!", kwargs["verbose"], Level.CRITICAL)
    pout(kwargs, kwargs["verbose"], Level.INFO)
    sort(kwargs, copyImage)
    pass

def mv(kwargs):
    """Move images to sorted directories."""
    pout("Not yet implemented!", kwargs["verbose"], Level.WARNING)
    pout(kwargs, kwargs["verbose"], Level.INFO)
    sort(kwargs, moveImage)
    pass
