from apiflask import APIFlask, Schema, input, output
from apiflask.fields import String


class LoginSchema(Schema):
    email = String()
    pwdhash = String()


class RegisterSchema(Schema):
    name = String()
    email = String()
    pwdhash = String()


app = APIFlask(__name__)

nextId = 2
users = [{
    'id': 1,
    'name': 'Justin Liu',
    'email': 'imbiansl@live.cn',
    'pwdhash': '$argon2id$v=19$m=1024,t=1,p=1$aW1iaWFuc2xAbGl2ZS5jbg$njAw0Hryny3nD6aSshpV86d6WkvpiUQ/'
}]


@app.post('/auth/login')
@input(LoginSchema)
def login(user):
    for registered_user in users:
        if user['email'] == registered_user['email'] and user['pwdhash'] == registered_user['pwdhash']:
            return {
                'id': registered_user['id'],
                'name': registered_user['name'],
                'pwdhash': registered_user['pwdhash'],
                'token': 123456
            }, 201
    return {
        'error': '用户名或密码错误。'
    }, 401


@app.post('/auth/register')
@input(RegisterSchema)
def register(user):
    global nextId
    for registered_user in users:
        if user['email'] == registered_user['email']:
            return {
                'error': '该邮箱已注册。'
            }, 400
    users.append({
        'id': nextId,
        **user
    })
    nextId = nextId + 1
    return {
        'id': nextId - 1,
        'name': user['name'],
        'email': user['email']
    }, 201
