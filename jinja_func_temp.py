from jinja2 import Environment, FileSystemLoader
import os.path
from log import log


# path = '{}/templates/'.format(os.path.dirname(__file__))
# # 得到加载模板的目录
# loader = FileSystemLoader(path)
# # 创建一个加载器，jinja从这个目录中加载模板
# env = Environment(loader)
# # 创建一个环境，用它来读取模板文件
#
# template = env.get_template('demo.html')


# 给temp_name（html模板名）和模板页面内的参数**kwargs，返回一个render后的页面
def template(temp_name, **kwargs):
    path = '{}/templates/'.format(os.path.dirname(__file__))
    loader = FileSystemLoader(path)
    env = Environment(loader=loader)
    html_page = env.get_template(temp_name)
    return html_page.render(**kwargs)


def response_with_headers(headers, status_code=200):
    header = "HTTP/1.1 {} OK\r\n".format(status_code)
    header += ''.join(["{}: {}\r\n".format(k, v) for k, v in headers.items()])
    return header


def redirect(path):
    headers = {
        'Content-Type': 'text/html',
        "Location": path,
    }
    header = response_with_headers(headers, 302)
    r = header + '\r\n' + ''
    return r.encode(encoding='utf-8')


# http响应函数，给与body，自动加上header并返回bytes页面
def http_response(body):
    headers = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n"
    r = headers + "\r\n" + body
    return r.encode(encoding='utf-8')