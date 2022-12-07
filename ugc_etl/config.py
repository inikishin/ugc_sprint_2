import logging
import sys

logger = logging.getLogger('etl.process')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
