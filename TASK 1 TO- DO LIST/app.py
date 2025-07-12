# app.py for TaskElevate Pro+

from flask import Flask, render_template, request, redirect, url_for, session
import json, os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'taskelevate_secret'

USER_FILE = os.path.join('data', 'users.json')
TODO_FILE = os.path.join('data', 'todos.json')

# ---------- Helper Functions ----------
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_todos(todos):
    with open(TODO_FILE, 'w') as f:
        json.dump(todos, f, indent=4)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

# ---------- Routes ----------
@app.route("/")
@login_required
def home():
    username = session['username']
    todos = load_todos().get(username, [])

    search = request.args.get("search", "").lower()
    priority = request.args.get("priority")
    category = request.args.get("category")
    sort_by = request.args.get("sort")

    # Filters
    if search:
        todos = [t for t in todos if search in t['name'].lower() or search in t['description'].lower()]
    if priority:
        todos = [t for t in todos if t['priority'] == priority]
    if category:
        todos = [t for t in todos if t['category'] == category]

    # Sorting
    if sort_by == "priority":
        todos.sort(key=lambda x: x['priority'])
    elif sort_by == "due":
        todos.sort(key=lambda x: x['due'])

    done = sum(1 for t in todos if t['checked'])
    return render_template("index.html", items=todos, completed=done, total=len(todos), user=username)

@app.route("/add", methods=["POST"])
@login_required
def add():
    todos = load_todos()
    username = session['username']
    form = request.form
    new_task = {
        "id": int(datetime.now().timestamp() * 1000),
        "name": form.get("todo_name"),
        "description": form.get("todo_description", ""),
        "due": form.get("todo_due", ""),
        "priority": form.get("todo_priority", "Medium"),
        "category": form.get("todo_category", ""),
        "checked": False,
        "subtasks": []
    }
    todos.setdefault(username, []).append(new_task)
    save_todos(todos)
    return redirect(url_for("home"))

@app.route("/toggle/<int:todo_id>", methods=["POST"])
@login_required
def toggle(todo_id):
    todos = load_todos()
    username = session['username']
    for todo in todos.get(username, []):
        if todo['id'] == todo_id:
            todo['checked'] = not todo['checked']
            break
    save_todos(todos)
    return redirect(url_for("home"))

@app.route("/delete/<int:todo_id>", methods=["POST"])
@login_required
def delete(todo_id):
    todos = load_todos()
    username = session['username']
    todos[username] = [t for t in todos.get(username, []) if t['id'] != todo_id]
    save_todos(todos)
    return redirect(url_for("home"))

@app.route("/edit/<int:todo_id>", methods=["POST"])
@login_required
def edit(todo_id):
    todos = load_todos()
    username = session['username']
    for todo in todos.get(username, []):
        if todo['id'] == todo_id:
            todo['name'] = request.form.get("todo_name")
            todo['description'] = request.form.get("todo_description")
            todo['due'] = request.form.get("todo_due")
            todo['priority'] = request.form.get("todo_priority")
            todo['category'] = request.form.get("todo_category")
            break
    save_todos(todos)
    return redirect(url_for("home"))

# ---------- Auth ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for("home"))
        return "Login failed. Try again."
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        users = load_users()
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return "Username already exists."
        users[username] = {"password": password}
        save_users(users)
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/logout")
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for("login"))

# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True)
