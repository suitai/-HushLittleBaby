#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import getopt
import urllib2

def download(url, out_dir, overwrite=False):
    file_name = url.split('/')[-1]
    out_dir = os.path.expanduser(out_dir)
    out_dir = os.path.expandvars(out_dir)
    out_file = "%s/%s" % (out_dir, file_name)

    if not os.path.isdir(out_dir):
        raise DownloadError("Cannot find directory \"%s\"." % out_dir)

    if os.path.exists(out_file) and not overwrite:
        raise DownloadError("The file \"%s\" is present." % out_file)

    urlopen = urllib2.urlopen(url)
    info = urlopen.info()
    file_size = int(info.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 4096
    with open(out_file, 'wb') as stream:
        while file_size:
            buffer = urlopen.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            stream.write(buffer)
            status = r"%10d/%10d  [%3.2f%%]" % (file_size_dl, file_size, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            print status,


class DownloadError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def main():
    out_dir = "."
    overwrite = False

    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'o:', ["overwrite"])
    except getopt.GetoptError as detail:
        sys.exit("GetoptError: %s" % detail)

    for opt, arg in optlist:
        if opt == "-o":
            out_dir = arg
        elif opt == "--overwrite":
            overwrite = True
        else:
            assert False, "unhandled option"
    try:
        download(args[0], out_dir, overwrite=overwrite)
    except DownloadError as detail:
        sys.exit("Error: %s" % detail)

### Execute
if __name__ == "__main__":
    main()
