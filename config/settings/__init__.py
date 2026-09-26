import os

env = os.getenv("DJANGO_ENV", "dev").lower()

if env == "prod":
    from .prod import *
elif env == "dev":
    from .dev import *
else:
    # Fallback to dev settings for unknown values
    from .dev import *
