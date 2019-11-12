import json
import boto3
import logging
from botocore.exceptions import ClientError

# Local imports
from .utils import GET_LAMBDA_FUNCTION_CONFIG, GET_CWL_STREAMS, GET_CWL_LOGS, LOG_GROUP_PREFIX


class LambdaLogCollector:
    def __init__(self, region, profile, function_name, start_time, end_time, pattern):
        self.region = region
        self.profile = profile
        self.function_name = function_name
        self.log_group_name = LOG_GROUP_PREFIX + function_name
        self.start_time = start_time
        self.end_time = end_time
        self.pattern = pattern
        self.session = boto3.Session(profile_name=profile, region_name=region)
        self.lambda_client = boto3.client("lambda")
        self.logs_client = boto3.client("logs")
        self.all_streams = []
        self.filtered_streams = []
        self.all_logs = []

        logging.debug("Log group name: %s" % self.log_group_name)

    def get_function_configuration(self):
        try:
            logging.info(GET_LAMBDA_FUNCTION_CONFIG)
            response = self.lambda_client.get_function_configuration(
                FunctionName=self.function_name
            )
            # logging.debug(json.dumps(response))
            del response["ResponseMetadata"]
            return json.dumps(response, indent=4)
        except ClientError as e:
            logging.error(e.response['Error']['Message'])
            return False

    def find_log_streams(self):
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

            logging.debug(self.filtered_streams)
            return json.dumps(self.filtered_streams, indent=4)
        except ClientError as e:
            logging.error("CloudWatch Log Group %s doesn't exist" % self.log_group_name)
            logging.error(e.response['Error']['Message'])
            return False

    def collect_logs(self):
        logging.info(GET_CWL_LOGS)
        paginator = self.logs_client.get_paginator("filter_log_events")
        if len(self.filtered_streams) > 0:
            page_iterator = paginator.paginate(
                logGroupName=self.log_group_name,
                logStreamNames=self.filtered_streams,
                startTime=self.start_time,
                endTime=self.end_time,
                filterPattern=self.pattern,
                limit=1500
            )

            try:
                for page in page_iterator:
                    self.all_logs += page.get("events")

                    logging.debug(self.all_logs)
                    return json.dumps(self.all_logs, indent=4)
            except ClientError as e:
                logging.error(e.response['Error']['Message'])
                return False
        else:
            logging.info("No CloudWatch Log stream match the criteria.")
            return False





