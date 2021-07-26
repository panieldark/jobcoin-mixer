import os
import sys
sys.path.insert(0, '/opt/bitnami/projects/jobcoin-mixer/djangomixer/')
os.environ.setdefault("PYTHON_EGG_CACHE", "/opt/bitnami/projects/jobcoin-mixer/djangomixer/egg_cache")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangomixer.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
