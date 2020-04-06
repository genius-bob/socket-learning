from jinja_func_temp import template, redirect, http_response
from models import JJTodo
from log import log, f_time


def index(request):
    todo_list = JJTodo.all()
    body = template('jinja_todo.html', todos=todo_list)
    return http_response(body)


def edit(request):
    edit_id = int(request.query.get('id', -1))
    t = JJTodo.find_by(id=edit_id)
    body = template('edit_todo.html', todos=t)
    return http_response(body)


def add(request):
    form = request.form()
    todo = JJTodo(form)
    todo.id = todo.create_id()
    todo.created_time = f_time()
    todo.save()
    return redirect('/jj')


def delete(request):
    del_id = request.query.get('id', '')
    JJTodo.delete(id=del_id)
    return redirect('/jj')


def update(request):
    upd_title = request.form().get('title', '')
    upd_id = int(request.query.get('id', -1))
    t = JJTodo.find_by(id=upd_id)
    t.title = upd_title
    t.save(True, 0, re1=1)
    return redirect('/jj')


jinja_todo_dict = {
    # 返回页面函数
    '/jj': index,
    '/jj/edit': edit,
    # 处理数据函数
    '/jj/add': add,
    '/jj/delete': delete,
    '/jj/update': update,
}