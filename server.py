"""
课 3 预习
2017/02/19


static 目录中存储了图片
templates 目录中存储了 html 文件
utils.py 包含了 log 函数
server.py 是扩展的服务器代码, 详细流程功能说明请看后文
routes.py 是服务器能处理的 path(路由) 和 路由处理函数
models.py 是数据存储的代码
"""
import socket
import urllib.parse
from log import log
from routes import route_static, route_dict
from routes_todo import todo_dict


class Request(object):

    def __init__(self):
        self.method = 'GET'
        self.path = ''
        self.body = ''
        self.query = {}
        self.headers = {}
        self.cookies = {}

    def add_cookies(self):
        cookie = self.headers.get('Cookie', '')
        cookies = cookie.split(';')
        for c in cookies:
            if '=' in c:
                k, v = c.split('=', 1)
                self.cookies[k] = v

    def add_headers(self, headers):
        for h in headers:
            k, v = h.split(':', 1)
            self.headers[k] = v
        self.cookies = {}
        self.add_cookies()

    def form(self):
        body = self.body
        args = body.split('&')
        f = {}
        for arg in args:
            k, v = arg.split('=')
            k, v = urllib.parse.unquote(k), urllib.parse.unquote(v)
            f[k] = v
        return f


request = Request()


def error(request, code=404):
    error_dict = {
        404: b"HTTP/1.1 404 not found\r\n\r\n<h1>Page Not Found</h1>\r\n",
    }
    return error_dict.get(code, b'')


def parsed_path(path):
    if '?' in path:
        path, query_str = path.split('?')
        query_str = query_str.split('&')
        query = {}
        for i in query_str:
            k, v = i.split('=')
            query[k] = v
    else:
        path, query = path, {}
    return path, query


def response_for_path(path):
    path, query = parsed_path(path)
    request.path = path
    request.query = query
    r = {
        '/static': route_static,
    }
    r.update(route_dict)
    r.update(todo_dict)
    response = r.get(path, error)
    return response(request)


def recv_all(conn):
    result = b''
    while True:
        r = conn.recv(1024)
        result += r
        if len(r) < 1024:
            break
    return result


def run(host='', port=3000):
    log('Start at:', 'Host:{} Port:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        while True:
            s.listen(5)
            connection, address = s.accept()
            r = recv_all(connection)
            r = r.decode('utf-8')
            log('raw request:', r)
            if len(r) < 2:
                continue
            path = r.split()[1]
            request.method = r.split()[0]
            log("请求的method：\n", request.method)
            request.body = r.split('\r\n\r\n', 1)[1]
            request.add_headers(r.split('\r\n\r\n')[0].split('\r\n')[1:])
            response = response_for_path(path)
            log('原始响应response:\n', response)
            connection.sendall(response)
            connection.close()


if __name__ == '__main__':
    config = dict(
        host='',
        port=3000,
    )
    run(**config)

"""
以下是课 3 的 server.py 的整理思路
server.py
    建立host和端口
    监听请求
    接受请求
        分解请求信息
            method
            path
            query
            body
        保存请求
            临时保存，用完就丢
    处理请求
        获取路由字典
            path和响应函数的映射字典
        根据请求的path和字典处理请求并获得返回页面
            routes
                主页
                    返回页面
                登录
                    处理post请求
                        对比post数据和用户数据
                        返回登录结果
                    返回页面
                注册
                    处理post请求
                        对比post数据和注册规则
                        保存合法的注册信息
                            保存到User.txt
                        返回注册结果
                    返回页面
                留言板
                    处理post请求
                        将post的数据加入留言列表
                    返回页面
                        包含留言列表
                静态资源（图片）
                    根据query的内容返回对应的资源
        返回响应内容
    发送响应内容
    关闭请求连接


"""
