
"""Logging backoff messages"""
import sys
import logging

logger = logging.getLogger('backoff_handler')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


def backoff_hdlr(details):
    """Print backoff details"""
    logger.warning("Backing off %s seconds after %s tries calling function %s "
                   "with args %s and kwargs %s",
                   details.get('wait'),
                   details.get('tries'),
                   details.get('target'),
                   details.get('args'),
                   details.get('kwargs'))