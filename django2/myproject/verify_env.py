import sys
import os

print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path}")

try:
    import django
    print(f"Django version: {django.get_version()}")
except ImportError:
    print("Django NOT found")

try:
    import rest_framework
    print("DRF found")
except ImportError:
    print("DRF NOT found")

try:
    import PIL
    from PIL import Image
    print(f"Pillow (PIL) version: {PIL.__version__}")
except ImportError:
    print("Pillow NOT found")

try:
    import google.generativeai
    print("google-generativeai found")
except ImportError as e:
    print(f"google-generativeai NOT found: {e}")

try:
    import MySQLdb
    print("mysqlclient (MySQLdb) found")
except ImportError:
    print("mysqlclient NOT found")

try:
    import requests
    print(f"requests version: {requests.__version__}")
except ImportError:
    print("requests NOT found")
