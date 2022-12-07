from gevent import monkey
monkey.patch_all()

from dotenv import load_dotenv
from auth.main import app

load_dotenv()
#  gunicorn --bind 0.0.0.0:5000 wsgi_app:app
