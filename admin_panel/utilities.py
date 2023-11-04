import datetime
from os.path import splitext


def get_timestamp_path(instance, filename):
    return '%s%s' % (datetime.datetime.now().timestamp(), splitext(filename)[1])