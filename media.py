from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(_name_)
app.secret_key = "secret123"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# DATABASE
def init_db():
    conn = sqlite3.connect("media.db")
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS press(id INTEGER PRIMARY KEY,title TEXT,date TEXT,description TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS coverage(id INTEGER PRIMARY KEY,title TEXT,url TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS gallery(id INTEGER PRIMARY KEY,image TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS videos(id INTEGER PRIMARY KEY,url TEXT)")

    conn.commit()
    conn.close()

init_db()


# LOGIN
@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        user=request.form["username"]
        pw=request.form["password"]

        if user=="admin" and pw=="admin":
            session["admin"]=True
            return redirect("/dashboard")

    return """
    <h2>Admin Login</h2>
    <form method="post">
    Username:<input name="username"><br>
    Password:<input type="password" name="password"><br>
    <button type="submit">Login</button>
    </form>
    """


# DASHBOARD
@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect("/")

    conn=sqlite3.connect("media.db")
    c=conn.cursor()

    press=c.execute("SELECT * FROM press").fetchall()
    coverage=c.execute("SELECT * FROM coverage").fetchall()
    images=c.execute("SELECT * FROM gallery").fetchall()
    videos=c.execute("SELECT * FROM videos").fetchall()

    conn.close()

    return render_template_string("""
    <h1>Manage Media Page</h1>

    <h2>Press Release</h2>
    <form method="post" action="/add_press">
    Title:<input name="title">
    Date:<input name="date">
    Description:<input name="description">
    <button>Add</button>
    </form>

    <ul>
    {% for p in press %}
    <li>{{p[1]}} - {{p[2]}} - {{p[3]}} 
    <a href="/delete_press/{{p[0]}}">Delete</a></li>
    {% endfor %}
    </ul>

    <h2>Media Coverage</h2>
    <form method="post" action="/add_coverage">
    Title:<input name="title">
    URL:<input name="url">
    <button>Add</button>
    </form>

    <ul>
    {% for c in coverage %}
    <li>{{c[1]}} - <a href="{{c[2]}}">View</a>
    <a href="/delete_cov/{{c[0]}}">Delete</a></li>
    {% endfor %}
    </ul>

    <h2>Image Gallery</h2>
    <form method="post" action="/add_image" enctype="multipart/form-data">
    <input type="file" name="image">
    <button>Upload</button>
    </form>

    {% for img in images %}
    <img src="/static/uploads/{{img[1]}}" width="100">
    <a href="/delete_img/{{img[0]}}">Delete</a>
    {% endfor %}

    <h2>Videos</h2>
    <form method="post" action="/add_video">
    Video URL:<input name="url">
    <button>Add</button>
    </form>

    <ul>
    {% for v in videos %}
    <li><a href="{{v[1]}}">View Video</a>
    <a href="/delete_video/{{v[0]}}">Delete</a></li>
    {% endfor %}
    </ul>
    """,press=press,coverage=coverage,images=images,videos=videos)


# ADD PRESS
@app.route("/add_press",methods=["POST"])
def add_press():
    conn=sqlite3.connect("media.db")
    c=conn.cursor()

    c.execute("INSERT INTO press(title,date,description) VALUES(?,?,?)",
              (request.form["title"],request.form["date"],request.form["description"]))

    conn.commit()
    conn.close()
    return redirect("/dashboard")


@app.route("/delete_press/<id>")
def delete_press(id):
    conn=sqlite3.connect("media.db")
    c=conn.cursor()
    c.execute("DELETE FROM press WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return redirect("/dashboard")


# ADD COVERAGE
@app.route("/add_coverage",methods=["POST"])
def add_coverage():
    conn=sqlite3.connect("media.db")
    c=conn.cursor()
    c.execute("INSERT INTO coverage(title,url) VALUES(?,?)",
              (request.form["title"],request.form["url"]))
    conn.commit()
    conn.close()
    return redirect("/dashboard")


@app.route("/delete_cov/<id>")
def delete_cov(id):
    conn=sqlite3.connect("media.db")
    c=conn.cursor()
    c.execute("DELETE FROM coverage WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return redirect("/dashboard")


# IMAGE
@app.route("/add_image",methods=["POST"])
def add_image():

    file=request.files["image"]
    filename=secure_filename(file.filename)
    file.save(os.path.join(app.config["UPLOAD_FOLDER"],filename))

    conn=sqlite3.connect("media.db")
    c=conn.cursor()
    c.execute("INSERT INTO gallery(image) VALUES(?)",(filename,))
    conn.commit()
    conn.close()

    return redirect("/dashboard")


@app.route("/delete_img/<id>")
def delete_img(id):
    conn=sqlite3.connect("media.db")
    c=conn.cursor()
    c.execute("DELETE FROM gallery WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return redirect("/dashboard")


# VIDEO
@app.route("/add_video",methods=["POST"])
def add_video():
    conn=sqlite3.connect("media.db")
    c=conn.cursor()
    c.execute("INSERT INTO videos(url) VALUES(?)",(request.form["url"],))
    conn.commit()
    conn.close()
    return redirect("/dashboard")


@app.route("/delete_video/<id>")
def delete_video(id):
    conn=sqlite3.connect("media.db")
    c=conn.cursor()
    c.execute("DELETE FROM videos WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return redirect("/dashboard")


if _name=="main_":
    app.run(debug=True)