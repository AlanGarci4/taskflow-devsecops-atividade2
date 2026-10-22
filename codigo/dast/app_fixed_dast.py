import json
import os
import sqlite3
from datetime import datetime, timezone

from flask import Flask, abort, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, template_folder="templates")

secret_key = os.environ.get("TASKFLOW_SECRET_KEY")
if not secret_key:
    raise RuntimeError(
        "Variavel TASKFLOW_SECRET_KEY nao definida. Configure-a antes de iniciar a app."
    )
app.config["SECRET_KEY"] = secret_key

DATABASE = os.environ.get("TASKFLOW_DB_PATH", "taskflow.db")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            done INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """
    )
    db.commit()

    cur = db.execute("SELECT COUNT(*) AS total FROM users")
    if cur.fetchone()["total"] == 0:
        db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", generate_password_hash("admin123")),
        )
        db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("aluno", generate_password_hash("senha123")),
        )
        db.commit()


def _log_event(event: str, **extra):
    payload = {
        "timestamp": _now_iso(),
        "event": event,
        "request_id": getattr(g, "request_id", None),
        "ip": request.headers.get("X-Forwarded-For", request.remote_addr),
        "method": request.method,
        "path": request.path,
    }
    payload.update(extra)
    print(json.dumps(payload, ensure_ascii=True))


@app.before_request
def set_request_id():
    g.request_id = request.headers.get("X-Request-ID") or os.urandom(8).hex()


@app.route("/healthz")
def healthz():
    return {"status": "ok"}, 200


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("tasks"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        db = get_db()
        cur = db.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            _log_event("login_success", username=username)
            return redirect(url_for("tasks"))

        error = "Usuario ou senha invalidos."
        _log_event("login_failed", username=username)

    # Error sink vai para template Jinja com autoescape ligado.
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    username = session.get("username")
    session.clear()
    _log_event("logout", username=username)
    return redirect(url_for("login"))


@app.route("/tasks", methods=["GET"])
def tasks():
    if "user_id" not in session:
        return redirect(url_for("login"))

    search = request.args.get("q", "")
    db = get_db()

    if search:
        like_pattern = f"%{search}%"
        rows = db.execute(
            "SELECT * FROM tasks WHERE user_id = ? AND title LIKE ?",
            (session["user_id"], like_pattern),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM tasks WHERE user_id = ?", (session["user_id"],)
        ).fetchall()

    _log_event("tasks_list", username=session.get("username"), count=len(rows), query=search)
    return render_template(
        "tasks.html", tasks=rows, username=session.get("username"), search=search
    )


@app.route("/tasks/new", methods=["GET", "POST"])
def new_task():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title", "")
        description = request.form.get("description", "")
        db = get_db()
        db.execute(
            "INSERT INTO tasks (user_id, title, description) VALUES (?, ?, ?)",
            (session["user_id"], title, description),
        )
        db.commit()
        _log_event("task_created", username=session.get("username"), title=title)
        return redirect(url_for("tasks"))

    return render_template("new_task.html")


@app.route("/debug/info")
def debug_info_removed():
    abort(404)


if __name__ == "__main__":
    with app.app_context():
        init_db()

    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
