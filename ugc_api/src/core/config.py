import os
import logging

logger = logging.getLogger('gunicorn.error')

PROJECT_NAME = os.getenv('PROJECT_NAME', 'ugc_api')

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
