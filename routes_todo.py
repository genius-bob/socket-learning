from models import Todo
from routes import response_with_header, template, redirect
from log import log


def index(request):
    headers = {
        'Content-Type': 'text/html',
    }
    models = Todo.all()
    # todo_html = ''.join(
    #     ['<h3>{}: {}</h3> <a href="/todo/edit?todo_id={}">编辑</a>\r\n'.format(m.id, m.title, m.id) for m in models])
    todo_html = ''
    for m in models:
        edit_html = '<a href="/todo/edit?todo_id={}">编辑</a>'.format(m.id)
        delete_html = '<a href="/todo/delete?todo_id={}">删除</a>'.format(m.id)
        todo_html += '<h3>{}: {}</h3>'.format(m.id, m.title) + edit_html + delete_html
    header = response_with_header(headers)
    body = template('/Todo.html')
    body = body.replace('{{ title }}', todo_html)
    r = header + '\r\n' + body
    return r.encode('utf-8')


def edit(request):
    headers = {
        'Content-Type': 'text/html',
    }
    todo_id = request.query.get('todo_id', '')
    log('edit请求的todo_id：', todo_id)
    todo = Todo.find_by(id=int(todo_id))
    todo_title = todo.title
    body = template('/todo_edit.html')
    body = body.replace('{{ todo_id }}', todo_id)
    body = body.replace('{{ todo_title }}', todo_title)
    header = response_with_header(headers)
    r = header + '\r\n' + body
    return r.encode('utf-8')


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
        todo.__dict__['title'] = todo_title
        todo.save(rewrite=True)
        log('update find_by修改后的属性：', todo.__dict__)
    return redirect('/todo')


def add(request):
    if request.method == 'POST':
        form = request.form()
        log('todo的request form：\n', form)
        t = Todo(form)
        t.save()
    return redirect('/todo')


def todo_delete(request):
    todo_id = request.query.get('todo_id', '')
    Todo.delete(id=int(todo_id))
    return redirect('/todo')


todo_dict = {
    # 显示函数
    '/todo': index,
    '/todo/edit': edit,
    # 数据处理路由
    '/todo/update': update,
    '/todo/add': add,
    '/todo/delete': todo_delete,
}
