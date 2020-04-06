import socket
import urllib.parse
from log import log
from routes import route_static, route_dict
from routes_todo import todo_dict
from jinja_todo import jinja_todo_dict


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
        self.headers = {}
        for h in headers:
            k, v = h.split(':', 1)
            self.headers[k] = v
        self.cookies = {}
        self.add_cookies()
        log('cookie:\n', self.cookies)

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
    r.update(jinja_todo_dict)
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

