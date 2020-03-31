import json
import boto3
import logging
from botocore.exceptions import ClientError

# Local imports
from .utils import split_streams, GET_LAMBDA_FUNCTION_CONFIG, GET_CWL_STREAMS, GET_CWL_LOGS, LOG_GROUP_PREFIX


class LambdaLogCollector:
    """
    Lambda Log Collector Class

    :param region (str):
    :param profile (str):
    :param function_name (str):
    :param start_time (int):
    :param end_time (int):
    :param pattern (str):
    """
    def __init__(self, region: str, profile: str, function_name: str, start_time: int, end_time: int, pattern: str):
        self.region = region
        self.profile = profile
        self.function_name = function_name
        self.log_group_name = LOG_GROUP_PREFIX + function_name
        self.start_time = start_time
        self.end_time = end_time
        self.pattern = pattern
        self.session = boto3.Session(profile_name=profile)
        self.lambda_client = boto3.client("lambda", region_name=region)
        self.logs_client = boto3.client("logs", region_name=region)
        self.all_streams = []
        self.filtered_streams = []
        self.all_logs = []

        logging.debug("Log group name: %s" % self.log_group_name)

    def get_function_configuration(self):
        """Get a Lambda Function configuration

        :return: Lambda Function Config Object or False
        """
        try:
            logging.info(GET_LAMBDA_FUNCTION_CONFIG)
            response = self.lambda_client.get_function_configuration(
                FunctionName=self.function_name
            )
            logging.debug(json.dumps(response))
            del response["ResponseMetadata"]
            return json.dumps(response, indent=4)
        except ClientError as e:
            logging.error(e.response['Error']['Message'])
            return False

    def find_log_streams(self):
        """Search for CloudWatch Log Streams based on start and end time

        :return: List of CloudWatch Log Streams or False
        """
        logging.info(GET_CWL_STREAMS)
        paginator = self.logs_client.get_paginator("describe_log_streams")
        page_iterator = paginator.paginate(
            logGroupName=self.log_group_name,
            orderBy="LastEventTime",
            limit=50
        )
        try:
            for page in page_iterator:
                self.all_streams += page.get("logStreams")

            filtered_streams = list(
                filter(lambda stream: self.start_time <= stream.get("creationTime") <= self.end_time,
                       self.all_streams)
            )
            self.filtered_streams = list(
                map(lambda stream: stream.get("logStreamName"), filtered_streams)
            )
            logging.info("Found %s log streams matching the criteria." % len(self.filtered_streams))
            logging.debug(self.filtered_streams)
            return json.dumps(self.filtered_streams, indent=4)
        except ClientError as e:
            logging.error("CloudWatch Log Group %s doesn't exist" % self.log_group_name)
            logging.error(e.response['Error']['Message'])
            return False

    def collect_logs(self):
        """Filter logs based on start, end time and filter pattern

        :return: List of CloudWatch Logs or False
        """
        logging.info(GET_CWL_LOGS)
        paginator = self.logs_client.get_paginator("filter_log_events")

        number_of_streams = len(self.filtered_streams)

        if number_of_streams > 0:
            chunks = list(split_streams(self.filtered_streams, 100))
            for chunk in chunks:
                page_iterator = paginator.paginate(
                    logGroupName=self.log_group_name,
                    logStreamNames=chunk,
                    startTime=self.start_time,
                    endTime=self.end_time,
                    filterPattern=self.pattern,
                    limit=1500
                )
                try:
                    for page in page_iterator:
                        self.all_logs.extend(page.get("events"))
                except ClientError as e:
                    logging.error(e.response['Error']['Message'])
                    return False

            logging.info("Found %s logs matching the %s pattern" % (len(self.all_logs), self.pattern))
            logging.debug(self.all_logs)
            return json.dumps(self.all_logs, indent=4)

        else:
            logging.info("No log matching the %s pattern." % self.pattern)
            return False






