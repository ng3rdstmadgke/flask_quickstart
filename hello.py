from flask import Flask, url_for, request
from markupsafe import escape


# 第一引数はモジュールorパッケージ名。
# テンプレートや静的ファイルなどをFlaskが探すときに利用される
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/<name>")
def hello(name):
    return f"Hello, {escape(name)}!"

# --- --- --- ルート変数 --- --- ---

# string: '/' 以外のすべてのテキストを受け付ける
@app.route("/user/<username>")
def show_user_profile(username: str):
    return f"User {escape(username)}"

# int: 正の整数を受け付ける
@app.route("/post/<int:post_id>")
def show_post(post_id: int):
    return f"Post {post_id}"

# path: '/' も含めてすべてのテキストを受け付ける
@app.route("/path/<path:subpath>")
def show_subpath(subpath):
    return f"Subpath {escape(subpath)}"

# --- --- --- URL末尾のスラッシュの扱い --- --- ---

# 末尾に '/' あり
# /projects/ : 200
# /projects  : /projects/ にリダイレクト
@app.route("/projects/")
def projects():
    return "The project page"

# 末尾に '/' なし
# /about/ : 404
# /about  : 200
@app.route("/about")
def about():
    return "The about page"

# --- --- --- URLの構築 --- --- ---

@app.route("/")
def index():
    return "index"

@app.route("/login")
def login():
    return "login"

@app.route("/user/<username>")
def profile(username):
    return f"{username}'s profile"

with app.test_request_context():
    print(url_for("index"))
    print(url_for("login"))
    print(url_for("login", next="/top"))
    print(url_for("profile", username="mido"))
    print(url_for("profile", username="mido", foo="bar"))

# --- --- --- HTTPメソッド --- --- ---

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        return "do the signin"
    else:
        return f'<form action="{url_for("signin")}" method="POST" ><input type="submit" value="signin"></form>'

# --- --- --- 静的ファイル --- --- ---

@app.route("/load_static_file")
def load_static_file():
    return f"""
<html><body>
  <link rel="stylesheet" href="{url_for("static", filename="style.css")}">
  <p>hello</p>
</body></html>
"""


# --- --- --- レンダリング --- --- ---
from flask import render_template

# jinja2を利用してテンプレートを処理
@app.route("/sample_tpl/")
@app.route("/sample_tpl/<name>")
def sample_tpl(name=None):
    return render_template("sample_tpl.html", name=name)


# --- --- --- リクエストデータ --- --- ---
from flask import request
def valid_login(username: str, password: str) -> bool:
    if username == "mido":
        return True
    else:
        return False

@app.route("/login_1", methods=["POST", "GET"])
def login_1():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if valid_login(username, password):
            return f'<p>username: {username}</p><p>password: {password}</p>'
        else:
            error = "Invalid username/password"
    return render_template("login.html", error=error)

# --- --- --- ファイルアップロード --- --- ---
from flask import request
from werkzeug.utils import secure_filename

@app.route("/upload_file", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # inputタグのname属性を指定してfileオブジェクトを取得
        f = request.files["the_file"]
        # 保存
        f.save("/tmp/upload_file.txt")
        # f.filenameでアップロードされたファイル名を取得できる。
        return f"{secure_filename(str(f.filename))} upload success !!"
    else:
        return f"""
<form method="POST" enctype="multipart/form-data" action="{url_for("upload_file")}">
    <input type="file" name="the_file">
    <input type="submit" value="upload">
</form>
"""

# --- --- --- Cookie --- --- ---
from flask import request, make_response

@app.route("/cookie")
def cookie():
    # cookieの読み取り
    username = request.cookies.get("username")
    # cookieの格納
    resp = make_response(render_template("cookie.html", username=username))
    resp.set_cookie("username", "midori")
    return resp

# --- --- --- リダイレクトとエラー --- --- ---
from flask import abort, render_template, redirect, url_for

# リダイレクト元
@app.route("/redirect_from")
def redirect_from():
    return redirect(url_for("redirect_to"))

# リダイレクト先
@app.route("/redirect_to")
def redirect_to():
    return "redirect!!!"

# 404エラーを返却する
@app.route("/not_found")
def not_found():
    abort(404)
    # not executed

# 404 エラーの場合のデフォルトページを定義
@app.errorhandler(404)
def page_not_found(error):
    return render_template("page_not_found.html"), 404


# --- --- --- レスポンス --- --- ---
from flask import make_response

@app.route("/bad_request")
def bad_request():
    abort(400)

# make_response()関数でレスポンスを生成
@app.errorhandler(400)
def page_bad_request(error):
    resp = make_response(render_template("bad_request.html"), 400)
    resp.headers["X-Something"] = "A Value"
    return resp


from flask import jsonify

# jsonを返却
@app.route("/me1")
def me_api_1():
    return {
        "username": "ktamido",
        "theme": "title",
        "image": url_for("bad_request", filename="image.png")
    }

# dict以外のデータをjsonで返したい場合はjsonify関数で明示的にresponseオブジェクトを生成
@app.route("/me2")
def me_api_2():
    d = [
        { "username": "mido" },
        { "username": "taku" },
        { "username": "mako" }
    ]
    return jsonify(d)

# --- --- --- セッション --- --- ---
from flask import session

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/top")
def top():
    if 'username' in session:
        return f"""
        <p>Logged in as {session["username"]}</p>
        <p><a href="{url_for("logout1")}">logout</a></p>
        """
    else:
        return f"""
        <p>You are not logged in</p>
        <p><a href="{url_for("login1")}">login</a></p>
        """

@app.route("/login1", methods=["GET", "POST"])
def login1():
    if request.method == "POST":
        session["username"] = request.form["username"]
        return redirect(url_for("top"))
    else:
        return f"""
        <form method="POST" >
            <input type="text" name="username">
            <input type="submit" value="login">
        </form>
        """

@app.route("/logout1")
def logout1():
    session.pop("username", None)
    return redirect(url_for("top"))


# --- --- --- ロギング --- --- ---
@app.route("/logger")
def logger():
    app.logger.debug('A value for debugging')
    app.logger.warning('A warning occurred (%d apples)', 42)
    app.logger.error('An error occurred')
    return "hello"