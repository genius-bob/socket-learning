import time


def log(*args, **kwargs):
    format = '%Y-%m-%d %H:%M:%S'
    realtime = time.strftime(format, time.localtime(time.time()))
    print(realtime, *args, **kwargs)
