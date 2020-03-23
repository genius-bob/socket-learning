from models import Messages
from models import User
from models import Cookie
from log import log


def template(route):
    path = 'templates' + route
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def route_register(request):
    header = 'HTTP/1.1 200 OK\r\nContent-Type=text/html\r\n'
    if request.method == 'POST':
        form = request.form()
        u = User(form)
        if u.register_validate():
            u.save()
            result = '注册成功<br><pre>{}</pre>'.format(User.all())
        else:
            result = '用户名或密码必须大于两位'
    else:
        result = ''
    body = template('/register.html')
    body = body.replace('{{result}}', result)
    r = header + '\r\n' + body
    return r.encode('utf-8')


def route_login(request):
    headers = {
        'Content-Type': 'text/html',
    }
    client = ''
    if request.method == 'POST':
        form = request.form()
        u = User(form)
        cookie = request.cookies.get(' user', '')
        c = Cookie({
            'name': u.username,
            'cookie': cookie, })
        client = current_user(request)
        if u.login_validate():
            result = '登陆成功'
            # 判断用户是否是已存在的，已存在的用户返回本地存储的cookie，不存在的返回新的cookie
            if c.the_same_user():
                headers['Set-Cookie'] = "user={}".format(c.the_same_user())
            else:
                cookie = c.random_str()
                c = Cookie({
                    'name': u.username,
                    'cookie': cookie, })
                c.save()
                headers['Set-Cookie'] = "user={}".format(c.cookie)
        else:
            result = '用户名或密码错误'
    else:
        result = ''
    body = template('/login.html')
    body = body.replace('{{result}}', result)
    body = body.replace('{{client}}', '你好，'+client)
    r = response_with_header(headers) + '\r\n' + body
    return r.encode('utf-8')


# 判断当前请求的用户是游客还是已登录用户
def current_user(request):
    cookie = request.cookies.get(' user', '')
    c = Cookie({
        'cookie': cookie,
    })
    return c.verify_cookie()


def route_static(request):
    filename = 'static/' + request.query.get('filename', 'doge.gif')
    header = b'HTTP/1.1 200 OK\r\nContent-Type: image/gif\r\n'
    with open(filename, 'rb') as f:
        img = header + b'\r\n' + f.read()
        return img


def route_index(request):
    header = 'HTTP/1.1 200 OK\r\nContent-Type= text/html\r\n\r\n'
    r = header + template('/index.html')
    return r.encode('utf-8')


def route_msg(request):
    if current_user(request) == '【游客】':
        header = 'HTTP/1.1 200 OK\r\nContent-Type= text/html\r\n'
        body = template('/login.html')
        r = header + '\r\n' + body
        return r.encode('utf-8')
    else:
        if request.method == 'POST':
            form = request.form()
            message = Messages(form)
            message.save()
        messages = '<br>'.join([str(m) for m in Messages.all()])
        body = template('/index_basic.html')
        body = body.replace('{{message}}', messages)
        header = 'HTTP/1.1 200 OK\r\nContent-Type= text/html\r\n'
        r = header + '\r\n' + body
        return r.encode('utf-8')


# 组合http请求的第一行和传入的headers(dict)项
def response_with_header(headers):
    header = 'HTTP/1.1 200 OK\r\n'
    header += ''.join(['{}: {}\r\n'.format(k, v) for k, v in headers.items()])
    return header


route_dict = {
    '/': route_index,
    '/register': route_register,
    '/login': route_login,
    '/msg': route_msg,
}