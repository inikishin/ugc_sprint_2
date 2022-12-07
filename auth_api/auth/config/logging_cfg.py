import logging
import sys

LOGGING_OUTPUT_FILE = '/data/log/output_print.log'
LOGGING_OUTPUT_FILE_SIZE = 10 # in Mb

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
logging_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s - %(lineno)s - %(message)s')
console_handler.setFormatter(logging_format)

 # File handler
file_handler = logging.handlers.RotatingFileHandler(
    LOGGING_OUTPUT_FILE,
    maxBytes=LOGGING_OUTPUT_FILE_SIZE * 1024 * 1024,
    backupCount=9)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging_format)
