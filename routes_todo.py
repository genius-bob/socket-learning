from models import Todo, User, Cookie
from routes import response_with_header, template, redirect, current_user
from log import log, f_time


def index(request):
    headers = {
        'Content-Type': 'text/html',
    }
    models = Todo.find_all(username=current_user(request))
    todo_html = ''
    for m in models:
        edit_html = '<a href="/todo/edit?todo_id={}">编辑 </a>'.format(m.id)
        delete_html = '<a href="/todo/delete?todo_id={}">删除</a>'.format(m.id)
        create_time_html = '<h3>创建时间:{}</h3> '.format(m.created_time)
        update_time_html = '<h3>修改时间:{}</h3> '.format(m.update_time)
        todo_html += '<h3>{}: {}</h3> '.format(m.id, m.title) + edit_html + delete_html + create_time_html\
                     + update_time_html
    header = response_with_header(headers)
    body = template('/Todo.html')
    body = body.replace('{{ title }}', todo_html)
    body = body.replace('{{ username }}', current_user(request))
    r = header + '\r\n' + body
    return r.encode('utf-8')


def index_admin(request):
    headers = {
        'Content-Type': 'text/html',
    }
    cookie = request.cookies.get(' user', '')
    c = Cookie.find_by(cookie=cookie)
    if c.name == 'ruanbo':
        models = User.all()
        todo_html = ''
        for m in models:
            id_html = '<h3>id:{}</h3> '.format(m.id)
            name_html = '<h3>用户:{}</h3> '.format(m.username)
            password_html = '<h3>密码:{}</h3> '.format(m.password)
            todo_html += id_html + password_html + name_html
        header = response_with_header(headers)
        body = template('/Todo.html')
        body = body.replace('{{ title }}', todo_html)
        body = body.replace('{{ username }}', current_user(request))
        r = header + '\r\n' + body
        return r.encode('utf-8')
    else:
        return redirect('/todo')


def edit(request):
    headers = {
        'Content-Type': 'text/html',
    }
    todo_id = request.query.get('todo_id', '')
    log('edit请求的todo_id：', todo_id)
    todo = Todo.find_by(id=int(todo_id))
    if todo:
        todo_title = todo.title
        body = template('/todo_edit.html')
        body = body.replace('{{ todo_id }}', todo_id)
        body = body.replace('{{ todo_title }}', todo_title)
        header = response_with_header(headers)
        r = header + '\r\n' + body
        return r.encode('utf-8')
    return redirect('/todo')


def update(request):
    header = {
        'Content-Type': 'text/html',
    }
    if request.method == 'POST':
        form = request.form()
        log('update的form：', form)
        todo_id = form.get('id', '')
        todo_title = form.get('title', '')
        todo = Todo.find_by(id=int(todo_id))
        log('update find_by的属性：', todo.__dict__)
        # todo.__dict__['title'] = todo_title
        todo.title = todo_title
        todo.update_time = f_time()
        todo.save(rewrite=True, judge_num=0, re1=1, re2=4)
        log('update find_by修改后的属性：', todo.__dict__)
    return redirect('/todo')


def add(request):
    if request.method == 'POST':
        form = request.form()
        log('todo的request form：\n', form)
        t = Todo(form)
        t.id = t.create_id()
        t.created_time = f_time()
        t.save()
    return redirect('/todo')


def todo_delete(request):
    todo_id = request.query.get('todo_id', '')
    cookie = request.cookies.get(' user', '')
    c = Cookie.find_by(cookie=cookie)
    todo = Todo.find_by(id=int(todo_id))
    if todo and todo.username != c.name:
        log("==========================u.username != usname")
        return redirect('/login')
    if todo_id:
        Todo.delete(id=int(todo_id))
        return redirect('/todo')


def login_require(route_func):
    def f(request):
        usname = current_user(request)
        if usname == '【游客】':
            return redirect('/login')
        return route_func(request)
    return f


todo_dict = {
    # 显示函数
    '/todo': login_require(index),
    '/todo/edit': edit,
    # 数据处理路由
    '/todo/update': update,
    '/todo/add': add,
    '/todo/delete': login_require(todo_delete),
    '/admin/users': login_require(index_admin),
}
