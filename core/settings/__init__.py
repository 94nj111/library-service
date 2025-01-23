import os

from dotenv import load_dotenv


load_dotenv()

environment = os.getenv("DJANGO_SETTINGS_MODULE", "core.settings.dev")

if environment == "core.settings.prod":
    from .prod import *
else:
    from .dev import *
