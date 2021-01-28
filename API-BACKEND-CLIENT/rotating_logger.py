from logging.handlers import RotatingFileHandler

import logging
import os
import zlib
import gzip
import sys

def namer(name):
    return name + ".gz"


def rotator(source, dest):
    # print(f'compressing {source} -> {dest}')
    # with open(source, "rb") as sf:
    #     data = sf.read()
    #     compressed = zlib.compress(data, 9)
    #     with open(dest, "wb") as df:
    #         df.write(compressed)
    # os.remove(source)
    try:
        old_log = open(source, 'rb')
        s = old_log.read()
        old_log.close()

        compressed_log = gzip.GzipFile(dest, 'wb', compresslevel=9)
        compressed_log.write(s)
        compressed_log.close()
        os.remove(source)
    except:
        print("Error compressing old log")
        sys.exit(-1)



def create_log(path, size, back_up_count, level):
    logger = logging.getLogger()
    logger.setLevel(level),
    handler = RotatingFileHandler(path, maxBytes=size, backupCount=back_up_count)
    handler.rotator = rotator
    handler.namer = namer
    handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
    logger.addHandler(handler)
    return logger