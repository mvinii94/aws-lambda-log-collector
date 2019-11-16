import click
from pathlib import Path

# Local imports
from .__init__ import *
from .utils import parse_time, create_dir, write_file, get_profiles, WRONG_PROFILE
from .lambda_log_collector import LambdaLogCollector


@click.command()
@click.version_option()
@click.option("--function-name", "-f", type=str, help="i.e. HelloWorld", required=True)
@click.option("--profile", "-p", type=str, help="AWS profile name (i.e. dev)", required=True)
@click.option("--region", "-r", type=str, help="AWS region (i.e. eu-west-1)", required=True)
@click.option("--output", "-o", type=click.Path(dir_okay=True, resolve_path=True), help="i.e. /tmp/", required=True)
@click.option("--start-time", "-s", type=str, help="2019-10-30T12:00:00", required=True)
@click.option("--end-time", "-e", type=str, help="2019-10-31T12:00:00", required=True)
@click.option("--pattern", type=str, help="ERROR", required=True)
@click.option("--log-level", type=click.Choice(['INFO', 'ERROR', 'DEBUG']), help='logging level', default='INFO')
def cli(function_name, profile, region, output, start_time, end_time, pattern, log_level):

    define_log_level(log_level)

    # get start and end time in epoch
    epoch_start_time = parse_time(start_time)
    epoch_end_time = parse_time(end_time)

    if profile not in get_profiles():
        raise Exception(WRONG_PROFILE % get_profiles)

    # initiate LambdaLogCollector class
    lambda_log_collector = LambdaLogCollector(region, profile, function_name, epoch_start_time, epoch_end_time, pattern)

    # get lambda function configuration
    lambda_configuration = lambda_log_collector.get_function_configuration()

    if lambda_configuration is not False:
        # find CloudWatch Logs between start_time and end_time
        streams = lambda_log_collector.find_log_streams()

        # collect logs from filtered log streams
        logs = lambda_log_collector.collect_logs()

        # replacing timestamp strings : to _ (windows support)
        start_time = start_time.replace(":", "_")
        end_time = end_time.replace(":", "_")

        # create output dir
        current_dir = Path(output)
        new_dir_name = function_name + "-" + start_time + "-" + end_time
        new_dir = Path(current_dir / new_dir_name)
        create_dir(new_dir)

        # write lambda config file
        lambda_fn_config_file = function_name + "-config.json"
        write_file(new_dir, lambda_fn_config_file, lambda_configuration)

        # write streams file
        if streams is not False:
            lambda_fn_streams_file = function_name + "-streams-" + start_time + "-" + end_time + ".json"
            write_file(new_dir, lambda_fn_streams_file, streams)

        # write logs file
        if logs is not False:
            lambda_fn_logs_file = function_name + "-logs-" + start_time + "-" + end_time + ".json"
            write_file(new_dir, lambda_fn_logs_file, logs)
