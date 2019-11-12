import setuptools
from collector.__init__ import __version__, __pkg_name__, __author__, __author_email__, __description__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=__pkg_name__,
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mvinii94/aws-lambda-log-collector",
    packages=["collector"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    keywords="aws lambda logs cloud",
    python_requires=">=3.6",
    install_requires=[
        "boto3<=1.10.14",
        "botocore<=1.13.14",
        "click>=7.0"
    ],
    entry_points='''
        [console_scripts]
        aws-lambda-log-collector=collector.cli:cli
    '''
)
