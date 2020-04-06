import time


def log(*args, **kwargs):
    format_time = '%Y-%m-%d %H:%M:%S'
    realtime = time.strftime(format_time, time.localtime(time.time()))
    with open('log.server.txt', 'a', encoding='utf-8') as f:
        print(realtime, *args, **kwargs, file=f)


def f_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
