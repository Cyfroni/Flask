from functools import wraps
from random import random
from flask import Flask, request, redirect, url_for, make_response, render_template
from flask.json import jsonify
from flask_basicauth import BasicAuth

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'Akwarysta69'
app.config['BASIC_AUTH_PASSWORD'] = 'J3si07r'

basic_auth = BasicAuth(app)

cookie = 0
fishes = dict()
counter = 1


def protected(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        cookie_secret = request.cookies.get('cookie_secret')
        if cookie == 0 or cookie_secret != cookie:
            return 'DENIED', 401
        return f(*args, **kwargs)

    return wrap


@app.route('/')
def main():
    return 'Hello, World!'


@app.route('/login', methods=['POST'])
def login():
    js = request.get_json()
    if not basic_auth.check_credentials(js['username'], js['password']):
        return "DENIED", 401

    global cookie
    cookie = str(random())

    resp = redirect(url_for('hello'))
    resp.set_cookie('cookie_secret', cookie)
    return resp


@app.route('/logout', methods=['POST'])
def logout():
    cookie_secret = request.cookies.get('cookie_secret')
    resp = make_response(
        render_template(
            'goodbye.html', name=cookie_secret
        )
    )
    resp.set_cookie('cookie_secret', '-')
    global cookie
    cookie = 0
    return resp


@app.route('/hello')
@protected
def hello():
    return render_template('hello.html', name=app.config['BASIC_AUTH_USERNAME'])


@app.route('/fishes', methods=['GET', 'POST'])
@protected
def fish1():
    if request.method == 'POST':
        new_fish = dict(request.get_json())
        global fishes, counter
        fishes[f'id_{counter}'] = new_fish
        counter += 1
        return f'fish added with id {counter - 1}'
    elif request.method == 'GET':
        return jsonify(fishes)


@app.route('/fishes/<id_>', methods=['GET', 'DELETE', 'PUT', 'PATCH'])
@protected
def fish2(id_):
    global fishes
    fish_id = f'id_{id_}'
    if fish_id not in fishes:
        return f"fish with id {id_} does not exist", 400

    if request.method == 'GET':
        return jsonify(fishes[fish_id])
    elif request.method == 'DELETE':
        fishes.pop(fish_id)
        return f'deleted fish with id {id_}'
    elif request.method == 'PUT':
        fishes[fish_id] = dict(request.get_json())
        return f'put fish with id {id_}'
    elif request.method == 'PATCH':
        patch = dict(request.get_json())
        for key, value in patch.items():
            fishes[fish_id][key] = value
        return f'patched fish with id {id_}'


# {
# 	"username" : "Akwarysta69",
# 	"password" : "J3si07r"
# }
#
# {
#     "who": "Znajomy",
#     "where": {
#         "lat": 0.001,
#         "long": 0.002
#     },
#     "mass": 34.56,
#     "length": 23.67,
#     "kind": "szczupak"
# }
# {
#     "who": "Kolega kolegi",
#     "where": {
#         "lat": 34.001,
#         "long": 52.002
#     },
#     "mass": 300.12,
#     "length": 234.56,
#     "kind": "sum olimpijczyk"
# }

@app.route("/my/request", methods=['POST', 'GET'])
@protected
def print_request():
    print(dir(request))
    print('request.args:', request.args)
    print('type(request.args):', type(request.args))
    print('request.query_string:', request.query_string)
    return ''


@app.route("/my/reset", methods=['DELETE'])
@protected
def reset():
    global fishes, counter
    fishes = dict()
    counter = 1
    return 'data reset'

# web: gunicorn app:app
# heroku ps:scale worker=1


if __name__ == '__main__':
    app.run(debug=True)
