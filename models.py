from log import log, f_time
import json
import random


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
        try:
            result = json.loads(s)
        except Exception:
            result = []
        return result


def save(data, path):
    s = json.dumps(data, indent=2, ensure_ascii=False)
    with open(path, 'w+', encoding='utf8') as f:
        f.write(s)


class Model(object):
    @classmethod
    def db_path(cls):
        path = 'db/{}.txt'.format(cls.__name__)
        return path

    @classmethod
    def all(cls):
        path = cls.db_path()
        models = load(path)
        ms = [cls(m) for m in models]
        return ms


    # rewrite参数为True时，例如username和id这类型的属性，如果出现重复，修改password和title的属性，而不是出现重复
    # **kwargs为要覆盖的属性处于self类的第几个位置，可以指定多个，如password处于User类的第二个属性，则"re1=1, rel2=2..."
    # judge_num为判断重复的属性的位置
    def save(self, rewrite=False, judge_num=0, **kwargs):
        path = self.db_path()
        models = self.models_dict_handle(self.all(), rewrite, judge_num, **kwargs)
        ss = [m.__dict__ for m in models]
        return save(ss, path)

    # 给Model类save方法创造密码和用户的方法，如果用户名username重复，替换该用户的密码，id不变

    def models_dict_handle(self, models, rewrite, judge_num, **kwargs):
        # if (hasattr(self, 'username') and hasattr(self, 'password')) or \
        #         (hasattr(self, 'id') and hasattr(self, 'title')) and len(models):
        #     index = -1
        #     for i, model in enumerate(models):
        #         if hasattr(model, 'username') and getattr(model, 'username') == getattr(self, 'username'):
        #             index = i
        #             break
        #         elif hasattr(model, 'id') and getattr(model, 'id') == getattr(self, 'id'):
        #             index = i
        #             break
        #     if index > -1 and hasattr(self, 'username') and hasattr(self, 'password'):
        #         models[index].__dict__['password'] = getattr(self, 'password')
        #     elif index > -1 and hasattr(self, 'id') and hasattr(self, 'title'):
        #         models[index].__dict__['title'] = getattr(self, 'title')
        #     else:
        #         models.append(self)
        if rewrite and len(models):
            index = -1
            first_dict = list(models[0].__dict__.keys())[judge_num]
            for i, model in enumerate(models):
                if hasattr(model, first_dict) and getattr(model, first_dict) == getattr(self, first_dict):
                    index = i
                    break
            if index > -1:
                for k, v in kwargs.items():
                    rewrite_dict = list(models[0].__dict__.keys())[v]
                    if hasattr(self, rewrite_dict):
                        models[index].__dict__[rewrite_dict] = getattr(self, rewrite_dict)
            else:
                models.append(self)
        else:
            models.append(self)
        return models

    # i.__dict__[k] 等价于 getattr(i, k)   i.__dict__.keys()等价于hasattr(i, k)
    @classmethod
    def find_by(cls, **kwargs):
        for i in cls.all():
            for k, v in kwargs.items():
                # if k in i.__dict__.keys() and i.__dict__[k] == v:
                if hasattr(i, k) and getattr(i, k) == v:
                    return i
        return None

    @classmethod
    def find_all(cls, **kwargs):
        result = []
        for i in cls.all():
            for k, v in kwargs.items():
                if hasattr(i, k) and getattr(i, k) == v:
                    # if k in i.__dict__.keys() and i.__dict__[k] == v:
                    result.append(i)
        return result

    @classmethod
    def create_id(cls):
        # cls.id = form.get('id', None)
        # if cls.id is not None:
        #     log("=============================cls.all()1", cls.id)
        #     cls.id = int(cls.id)
        # else:
        if not cls.all():
            log("=============================cls.all()2")
            cls.id = 1
        else:
            log("=============================cls.all()3")
            cls.id = cls.all()[-1].__dict__['id'] + 1
        return cls.id

    def __repr__(self):
        classname = self.__class__.__name__
        properties = ['{}:({})'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '< {}\n{}\n >\n'.format(classname, s)

    @classmethod
    def delete(cls, **kwargs):
        path = cls.db_path()
        models = cls.all()
        for k, v in kwargs.items():
            for i, m in enumerate(models):
                if not hasattr(m, k):
                    continue
                if str(getattr(m, k)) == str(v):
                    del models[i]
                    break
        ll = [m.__dict__ for m in models]
        save(ll, path)


class Messages(Model):
    def __init__(self, form):
        self.author = form.get('author', '')
        self.message = form.get('message', '')


class User(Model):
    def __init__(self, form):
        self.id = form.get('id', '')
        self.username = form.get('username', '')
        self.password = form.get('password', '')

    def login_validate(self):
        for i in self.all():
            if self.username == getattr(i, 'username') and self.password == getattr(i, 'password'):
                return True
        return False

    def register_validate(self):
        return len(self.username) > 2 and len(self.password) > 2


class Cookie(Model):
    def __init__(self, cookie_form: object) -> object:
        self.name = cookie_form.get('name', '')
        self.cookie = cookie_form.get('cookie', '')

    def verify_cookie(self):
        models = self.all()
        for m in models:
            if getattr(m, 'cookie') == self.cookie:
                return getattr(m, 'name')
        return '【游客】'

    def random_str(self):
        seed = "abcdefghijklmnopqrstuvwxyz"
        s = ''
        for i in range(20):
            random_index = random.randint(0, len(seed) - 1)
            s += seed[random_index]
        return s

    # 判断已存在的user，不重新给与cookie，重复用户，返回cookie值，不重复返回None
    def the_same_user(self):
        models = self.all()
        for m in models:
            if getattr(m, 'name') == self.name:
                return getattr(m, 'cookie')
        return None


class Todo(Model):
    def __init__(self, form):
        log("=============================form:", form)
        self.id = form.get('id', '')
        self.title = form.get('title', '')
        self.username = form.get('username', '')
        self.created_time = form.get('created_time', '')
        self.update_time = form.get('update_time', '')


class JJTodo(Model):
    def __init__(self, form):
        self.id = form.get('id', '')
        self.title = form.get('title', '')
        self.created_time = form.get('created_time', '')
