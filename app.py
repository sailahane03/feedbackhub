from flask import Flask, render_template, request, redirect, session
from db import init_db, get_db
from models import authenticate_user, submit_feedback
import random
import string

app = Flask(__name__)
app.secret_key = "super-secret-key"

init_db()

def generate_captcha():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=5))


@app.route("/", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "GET":
        session["captcha"] = generate_captcha()
        return render_template("login.html", captcha=session["captcha"], error=None)

    if request.form.get("captcha") != session.get("captcha"):
        error = "Invalid CAPTCHA"
        session["captcha"] = generate_captcha()
        return render_template("login.html", captcha=session["captcha"], error=error)

    user = authenticate_user(
        request.form.get("username"),
        request.form.get("password", "")
    )

    if not user:
        error = "Invalid credentials"
        session["captcha"] = generate_captcha()
        return render_template("login.html", captcha=session["captcha"], error=error)

    session["user_id"] = user["id"]
    session["role"] = user["role"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO login_logs (user_id) VALUES (?)", (user["id"],))
    conn.commit()
    conn.close()

    return redirect("/admin" if user["role"] == "admin" else "/feedback")


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        try:
            from models import create_user
            create_user(
                request.form["username"],
                request.form["password"]
            )
            return redirect("/")
        except Exception:
            error = "Username already exists"

    return render_template("register.html", error=error)


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if session.get("role") != "user":
        return redirect("/")

    if request.method == "POST":
        submit_feedback(
            session["user_id"],
            request.form["subject"],
            request.form["rating"],
            request.form["comments"]
        )

    return render_template("feedback.html")


@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT u.username, l.login_time
        FROM login_logs l JOIN users u ON l.user_id = u.id
        ORDER BY l.login_time DESC
    """)

    logins = cur.fetchall()

    cur.execute("""
        SELECT u.username, f.subject, f.rating, f.comments, f.timestamp
        FROM feedback f JOIN users u ON f.user_id = u.id
    """)
    feedbacks = cur.fetchall()

    cur.execute("SELECT username, role, password_hash FROM users")
    users = cur.fetchall()

    conn.close()

    return render_template("admin.html", logins=logins, feedbacks=feedbacks, users=users)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
