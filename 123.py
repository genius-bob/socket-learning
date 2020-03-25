from models import Todo
k = list(Todo.all()[0].__dict__.keys())[0]
print(k)