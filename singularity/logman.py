import logging
import os
import sys

class Logman:

    def __init__(self,stream=True,MESSAGELEVEL=None):
        self.level = get_logging_level(MESSAGELEVEL)
        if stream == True:
            logging.basicConfig(stream=sys.stdout,level=self.level)
        else:
            logging.basicConfig(level=self.level)
        self.logger = logging.getLogger('shub_builder')
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_logging_level(MESSAGELEVEL=None):
    '''get_logging_level will return a logging level based on first
    a variable going into the function, then an environment variable
    MESSAGELEVEL, and then the default is DEBUG.
    :param MESSAGELEVEL: the level to get.
    '''
    if MESSAGELEVEL == None:
        MESSAGELEVEL = os.environ.get("MESSAGELEVEL","DEBUG")

    if MESSAGELEVEL in ["DEBUG","INFO"]:
        print("Environment message level found to be %s" %MESSAGELEVEL)

    if MESSAGELEVEL == "FATAL":
        return logging.FATAL

    elif MESSAGELEVEL == "CRITICAL":
        return logging.CRITICAL

    elif MESSAGELEVEL == "ERROR":
        return logging.ERROR

    elif MESSAGELEVEL == "WARNING":
        return logging.WARNING

    elif MESSAGELEVEL == "INFO":
        return logging.INFO

    elif MESSAGELEVEL in "DEBUG":
        return logging.DEBUG

    return logging.DEBUG

bot = Logman()
