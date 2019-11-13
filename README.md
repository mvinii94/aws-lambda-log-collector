# AWS Lambda Log Collector

If you usually find yourself trying to debug AWS Lambda Functions and getting lost when trying to search for logs,
this CLI is meant for you.

Imagine your Lambda Function had an invocation error spike during last night. Today after arriving at your company you 
need to troubleshoot that error spike. You usually need to open CloudWatch Logs console and start to scroll infinitely
through the Log Streams, even worse if the Lambda Function has millions of invocations daily.

This CLI will help you to gather all the useful CloudWatch Logs from a Lambda Function, with a single command while
you can go for your morning coffee.

**Why?**

Because you can search for a subset of the these logs providing a start and end time, and even better you can also
provide a [CloudWatch Logs Filter Pattern]((https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/FilterAndPatternSyntax.html)). 
Making it easier to find what you are looking for!

### Usage

```bash
Usage: aws-lambda-log-collector [OPTIONS]

Options:
  --version                       Show the version and exit.
  -f, --function-name TEXT        i.e. HelloWorld  [required]
  -p, --profile TEXT              AWS profile name (i.e. dev)  [required]
  -r, --region TEXT               AWS region (i.e. eu-west-1)  [required]
  -o, --output PATH               i.e. /tmp/  [required]
  -s, --start-time TEXT           2019-10-30T12:00:00  [required]
  -e, --end-time TEXT             2019-10-31T12:00:00  [required]
  --pattern TEXT                  ERROR  [required]
  --log-level [INFO|ERROR|DEBUG]  logging level
  --help                          Show this message and exit.
```

### Parameters

#### --function-name || -f
The desired Lambda Function Name you want to retrieve logs from.

#### --start-time || -s 
The start of the time range where the CLI search for logs, CloudWatch Logs with a timestamp before this time are not
returned. 
> Pattern: YYYY-mm-ddThh:MM:ss

#### --end-time || -e
The end of the time range where the CLI search for logs, CloudWatch Logs with a timestamp after this time are not
returned.
> Pattern: YYYY-mm-ddThh:MM:ss

#### --pattern
The filter pattern to use while searching for logs content. You can use CloudWatch Logs
[Filter and Pattern Syntax](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/FilterAndPatternSyntax.html).

#### --output || -o
The output path where the CLI will store the logs.

#### --region || -r
The AWS Region where you Lambda Function belongs to.

#### --profile || -p
A configured aws [profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html).

### Installation

#### From pip

```bash
pip install aws-lambda-log-collector
```

#### From source

```bash
git clone https://github.com/mvinii94/aws-lambda-log-collector && cd aws-lambda-log-collector

pip install -e .
```

### Sample

```bash
aws-lambda-log-collector --function-name MyFunction \
--start-time 2019-11-10T23:30:00 --end-time 2019-11-11T03:30:00 \
--pattern "ERROR" --output /tmp/ --region eu-west-1 --profile dev
```

