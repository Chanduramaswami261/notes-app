import os
import psycopg2
from flask import Flask, request, redirect
from markupsafe import escape

app = Flask(__name__)

def conn():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["POSTGRESQL_DATABASE"],
        user=os.environ["POSTGRESQL_USER"],
        password=os.environ["POSTGRESQL_PASSWORD"],
    )

def init_db():
    with conn() as c, c.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS notes (id serial PRIMARY KEY, body text)")

@app.route("/healthz")
def healthz():
    return "ok"

@app.route("/ready")
def ready():
    with conn() as c, c.cursor() as cur:
        cur.execute("SELECT 1")
    return "ready"

@app.route("/", methods=["GET", "POST"])
def index():
    init_db()
    if request.method == "POST":
        with conn() as c, c.cursor() as cur:
            cur.execute("INSERT INTO notes (body) VALUES (%s)", (request.form["body"],))
        return redirect("/")
    with conn() as c, c.cursor() as cur:
        cur.execute("SELECT body FROM notes ORDER BY id DESC")
        rows = cur.fetchall()
    items = "".join(f"<li>{escape(r[0])}</li>" for r in rows)
    title = os.environ.get("APP_TITLE", "Notes")
    return (f"<h1>{escape(title)}</h1>"
            "<form method='post'><input name='body'><button>Add</button></form>"
            f"<ul>{items}</ul>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)