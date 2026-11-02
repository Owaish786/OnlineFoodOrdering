import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "super_secret_key"

def get_db():
    conn = sqlite3.connect("library.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM books")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO books (title, author) VALUES (?, ?)", [
            ("Clean Code", "Robert C. Martin"),
            ("The Pragmatic Programmer", "Andrew Hunt"),
            ("DevOps Handbook", "Gene Kim")
        ])
    conn.commit()
    conn.close()

def calculate_fine(overdue_days):
    if overdue_days < 0:
        raise ValueError("Overdue days cannot be negative")
    return overdue_days * 5

@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    conn = get_db()
    if query:
        books = conn.execute("SELECT * FROM books WHERE title LIKE ?", (f"%{query}%",)).fetchall()
    else:
        books = conn.execute("SELECT * FROM books").fetchall()
    conn.close()
    return render_template("index.html", books=books, query=query, username=session.get("username"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash("Registration successful! Please login.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists!")
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()
        if user:
            session["username"] = user["username"]
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)

