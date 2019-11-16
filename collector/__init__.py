"""
Lambda Log Collector
"""
import logging

FORMAT = '[%(levelname)s] - %(asctime)s - %(message)s'


def define_log_level(level):
    if "ERROR" == level:
        logging.basicConfig(level=logging.ERROR, format=FORMAT, datefmt='%m/%d/%Y %I:%M:%S')
    if 'DEBUG' == level:
        logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%m/%d/%Y %I:%M:%S')
    if 'INFO' == level:
        logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt='%m/%d/%Y %I:%M:%S')


__pkg_name__ = "aws-lambda-log-collector"

__version__ = "0.0.6"

__description__ = "A handy CLI to help you gather Lambda Functions logs"

__author__ = "Marcus Ramos"

__author_email__ = "marcusramos@outlook.ie"
