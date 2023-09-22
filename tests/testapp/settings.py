# minimal settings for running tests

SECRET_KEY = "Some secret key"

# CELERY_ALWAYS_EAGER = True

EVENT_SIGNALS_CELERY_APP = "tests.testapp.celery.app"
