import time


def log(*args, **kwargs):
    format = '%Y-%m-%d %H:%M:%S'
    realtime = time.strftime(format, time.localtime(time.time()))
    print(realtime, *args, **kwargs)


def f_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
