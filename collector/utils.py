import os
import boto3
import logging
import zipfile
import botocore.session
from pathlib import Path
from time import mktime, strptime
from botocore.exceptions import ClientError

LOG_GROUP_PREFIX = "/aws/lambda/"
GET_LAMBDA_FUNCTION_CONFIG = "Trying to get Lambda Function configuration..."
GET_CWL_STREAMS = "Trying to get CloudWatch Logs Streams..."
GET_CWL_LOGS = "Trying to collect logs from CloudWatch Logs..."
DESCRIPTION = """
                AWS Lambda Log Collector - 
                Easily gather and filter Lambda Function Logs stored in CloudWatch Logs
              """
INVALID_PROFILE = "[Error] - The provided profile is not configured. The configured profiles are: %s"
INVALID_DATES = "[Error] - Start timestamp must be before End timestamp"


def get_profiles():
    """Get configured profiles from botocore.session

    :return: List of configured profiles
    """
    session_list = botocore.session.get_session()
    profiles = session_list.available_profiles
    logging.debug("Configured profiles:")
    logging.debug(profiles)

    return profiles


def parse_time(date: str):
    """Parse a string date (format %Y-%m-%dT%H:%M:%S) into epoch

    :param date: Base path where the new directory will be created
    :return: Epoch date
    """
    date = int(mktime(strptime(date, '%Y-%m-%dT%H:%M:%S'))) * 1000
    return date


def create_dir(path: str):
    """Create a directory in the filesystem

    :param path: Base path where the new directory will be created
    :return: True or False
    """
    logging.info("Output path: %s" % path)
    try:
        dir_location = Path(path)
        os.makedirs(dir_location)
        return True
    except OSError:
        return False


def write_file(path: str, file_name: str, content: str):
    """Write a file in the filesystem

    :param path: Path where the file will be saved
    :param file_name: The filename to be created
    :param content: The file content
    :return: True or False
    """
    logging.info("Saving file %s..." % file_name)
    file_name = Path(path / file_name)
    try:
        file = open(file_name, 'w')
        file.write(content)
        return True
    except FileNotFoundError as e:
        logging.error("File not found (%s): %s" % (e.errno, e.strerror))
        return False
    except IOError as e:
        logging.error("I/O error(%s): %s" % (e.errno, e.strerror))
        return False
    finally:
        file.close()


def split_streams(streams: list, max_items: int):
    """Split a list of streams into chunks

    :param streams: List to be split
    :param max_items: Max number of items
    :return: Generator
    """
    for item in range(0, len(streams), max_items):
        yield streams[item:item + max_items]


def upload_file(file_name: str, bucket: str, object_name: str):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True or False
    """

    if object_name is None:
        object_name = file_name

    s3 = boto3.client("s3")

    try:
        response = s3.upload_file(file_name, bucket, object_name)
        logging.debug(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def compress(zip_path, file_name):
    """Compress a directory

    :param zip_path: The path to be zipped
    :param file_name: The output path where the zipfile will be created
    :return: True or False
    """
    try:
        logging.info("Trying to compress the output files...")
        zip_file = zipfile.ZipFile(file_name + ".zip", mode='w')
        for root, _, files in os.walk(zip_path):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.basename(file_path))

        logging.info("Logs output file at %s.zip" % file_name)
        return True
    except FileNotFoundError as e:
        logging.error("File not found (%s): %s" % (e.errno, e.strerror))
        return False
    except IOError as e:
        logging.error("I/O error(%s): %s" % (e.errno, e.strerror))
        return False
    finally:
        zip_file.close()

