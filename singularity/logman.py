import io
import os
import logging

class Logman:

    def __init__(self,MESSAGELEVEL=None):
        self.level = get_logging_level(MESSAGELEVEL)
        logging.basicConfig(level=self.level)
        self.logger = logging.getLogger('shub_builder')
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.capture = io.StringIO()

    def start(self):
        self.ch = logging.StreamHandler(self.capture)
        self.ch.setLevel(self.level)
        self.ch.setFormatter(self.formatter)
        self.logger.addHandler(self.ch)

    def stop(self):
        ### Pull the contents back into a string and close the stream
        self.contents = self.capture.getvalue()
        self.capture.close()
        return self.contents


def get_logging_level(MESSAGELEVEL=None):
    '''get_logging_level will return a logging level based on first
    a variable going into the function, then an environment variable
    MESSAGELEVEL, and then the default is DEBUG.
    :param MESSAGELEVEL: the level to get.
    '''
    if MESSAGELEVEL == None:
        MESSAGELEVEL = os.environ.get("MESSAGELEVEL","DEBUG")

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
bot.start()
