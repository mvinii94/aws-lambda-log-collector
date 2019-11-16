import os
import logging
import botocore.session
from time import mktime, strptime

LOG_GROUP_PREFIX = "/aws/lambda/"
WRONG_PROFILE = "[Error] - The provided profile is not configured. The configured profiles are: %s"
GET_LAMBDA_FUNCTION_CONFIG = "Trying to get Lambda Function configuration..."
GET_CWL_STREAMS = "Trying to get CloudWatch Logs Streams..."
GET_CWL_LOGS = "Trying to collect logs from CloudWatch Logs..."
DESCRIPTION = """
                AWS Lambda Log Collector - 
                Easily gather and filter Lambda Function Logs stored in CloudWatch Logs
              """


def get_profiles():
    session_list = botocore.session.get_session()
    profiles = session_list.available_profiles
    logging.debug("Profiles:")
    logging.debug(profiles)

    return profiles


def parse_time(date):
    date = int(mktime(strptime(date, '%Y-%m-%dT%H:%M:%S'))) * 1000
    return date


def create_dir(path):
    logging.info("Output path: %s" % path)
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise


def write_file(file_name, content):
    logging.info("Saving file %s..." % file_name)
    file = open(file_name, 'w')
    try:
        file.write(content)
    finally:
        file.close()


def split_list(l, n):
    for item in range(0, len(l), n):
        yield l[item:item + n]
