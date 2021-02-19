from logging.handlers import RotatingFileHandler
from pathlib import Path

import logging
import os
import gzip
import sys


def namer(name):
    return name + ".gz"


def rotator(source, dest):
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


def create_log(path, file_name, size, backup_count, level):
    logger = logging.getLogger()
    logger.setLevel(level),
    handler = None
    try:
        handler = create_handler(path+file_name, size, backup_count)
    except FileNotFoundError:
        Path(path).mkdir(parents=True, exist_ok=True)
        file = open(file_name, "w")
        file.close()
        handler = create_handler(path+file_name, size, backup_count)
    logger.addHandler(handler)
    return logger


def create_handler(path, size, backup_count):
    handler = RotatingFileHandler(path, maxBytes=size, backupCount=backup_count)
    handler.rotator = rotator
    handler.namer = namer
    handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
    return handler


def create_log_fro_config(logger_config):
    print(logger_config)
    return False
