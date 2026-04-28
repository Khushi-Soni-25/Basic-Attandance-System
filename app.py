import csv
import os
import re
import sqlite3
from datetime import datetime
from io import StringIO
from pathlib import Path
from xml.sax.saxutils import escape

from flask import Flask, Response, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "local-dev-secret-key")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = Path(os.environ.get("DB_PATH", BASE_DIR / "attendance.db"))
ALLOWED_STATUSES = {
    "Present",
    "First Half Leave",
    "Second Half Leave",
    "Holiday",
    "Absent",
}


def sanitize_username(username):
    return re.sub(r"[^a-zA-Z0-9_-]", "", username)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_FILE)
        g.db.row_factory = sqlite3.Row

    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                full_name TEXT,
                company_name TEXT
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                date TEXT,
                status TEXT,
                note TEXT,
                UNIQUE(user_id, date),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        db.commit()


def is_valid_date(date_text):
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
    except (TypeError, ValueError):
        return False

    return True


def get_user_by_username(username):
    if not username:
        return None

    return get_db().execute(
        "SELECT * FROM users WHERE username = ?",
        (username,),
    ).fetchone()


def get_current_user():
    username = session.get("username")
    user = get_user_by_username(username)

    if not user:
        return None

    return user


def get_user_records(user_id):
    rows = get_db().execute(
        """
        SELECT date, status, note
        FROM attendance
        WHERE user_id = ?
        ORDER BY date DESC
        """,
        (user_id,),
    ).fetchall()

    return {
        row["date"]: {
            "date": row["date"],
            "status": row["status"],
            "note": row["note"] or "",
        }
        for row in rows
    }


init_db()


@app.route("/")
def index():
    if not get_current_user():
        return redirect(url_for("login"))

    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = sanitize_username(request.form.get("username", "").strip())
        password = request.form.get("password", "")
        user = get_user_by_username(username)

        if user and check_password_hash(user["password"], password):
            session["username"] = username
            return redirect(url_for("index"))

        return render_template("login.html", error="Invalid username or password")

    if get_current_user():
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = sanitize_username(request.form.get("username", "").strip())
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "").strip()
        company_name = request.form.get("company_name", "").strip()

        if not username or not password:
            return render_template("register.html", error="Username and password are required")

        if get_user_by_username(username):
            return render_template("register.html", error="Username already exists")

        db = get_db()
        db.execute(
            """
            INSERT INTO users (username, password, full_name, company_name)
            VALUES (?, ?, ?, ?)
            """,
            (username, generate_password_hash(password), full_name, company_name),
        )
        db.commit()

        return redirect(url_for("login"))

    if get_current_user():
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/profile-info", methods=["GET"])
def profile_info():
    user = get_current_user()

    if not user:
        return jsonify({"success": False, "error": "Login required"}), 401

    return jsonify({
        "username": user["username"],
        "full_name": user["full_name"] or "",
        "company_name": user["company_name"] or "",
    })


@app.route("/get-records", methods=["GET"])
def get_records():
    user = get_current_user()

    if not user:
        return jsonify({"success": False, "error": "Login required"}), 401

    return jsonify(get_user_records(user["id"]))


@app.route("/save-record", methods=["POST"])
def save_record():
    user = get_current_user()

    if not user:
        return jsonify({"success": False, "error": "Login required"}), 401

    data = request.get_json(silent=True) or {}

    date = data.get("date")
    status = data.get("status")
    note = data.get("note", "")

    if not date:
        return jsonify({"success": False, "error": "Date is required"}), 400

    if not is_valid_date(date):
        return jsonify({"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}), 400

    if status not in ALLOWED_STATUSES:
        return jsonify({"success": False, "error": "Invalid status"}), 400

    if note is None:
        note = ""

    record = {
        "date": date,
        "status": status,
        "note": str(note),
    }

    db = get_db()
    db.execute(
        """
        INSERT INTO attendance (user_id, date, status, note)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, date)
        DO UPDATE SET status = excluded.status, note = excluded.note
        """,
        (user["id"], record["date"], record["status"], record["note"]),
    )
    db.commit()

    return jsonify({
        "success": True,
        "message": "Record saved successfully",
        "record": record,
    })


@app.route("/export-csv", methods=["GET"])
def export_csv():
    user = get_current_user()

    if not user:
        return redirect(url_for("login"))

    records = get_user_records(user["id"])
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["Date", "Status", "Note"])

    for date, record in records.items():
        writer.writerow([
            record.get("date", date),
            record.get("status", ""),
            record.get("note", ""),
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=attendance_{user['username']}.csv"
        },
    )


@app.route("/export-xml", methods=["GET"])
def export_xml():
    user = get_current_user()

    if not user:
        return redirect(url_for("login"))

    records = get_user_records(user["id"])
    rows = [
        "<Row>"
        "<Cell><Data ss:Type=\"String\">Date</Data></Cell>"
        "<Cell><Data ss:Type=\"String\">Status</Data></Cell>"
        "<Cell><Data ss:Type=\"String\">Note</Data></Cell>"
        "</Row>"
    ]

    for date, record in records.items():
        rows.append(
            "<Row>"
            f"<Cell><Data ss:Type=\"String\">{escape(record.get('date', date))}</Data></Cell>"
            f"<Cell><Data ss:Type=\"String\">{escape(record.get('status', ''))}</Data></Cell>"
            f"<Cell><Data ss:Type=\"String\">{escape(record.get('note', ''))}</Data></Cell>"
            "</Row>"
        )

    xml_content = (
        "<?xml version=\"1.0\"?>"
        "<?mso-application progid=\"Excel.Sheet\"?>"
        "<Workbook xmlns=\"urn:schemas-microsoft-com:office:spreadsheet\" "
        "xmlns:ss=\"urn:schemas-microsoft-com:office:spreadsheet\">"
        "<Worksheet ss:Name=\"Attendance\">"
        "<Table>"
        f"{''.join(rows)}"
        "</Table>"
        "</Worksheet>"
        "</Workbook>"
    )

    return Response(
        xml_content,
        mimetype="application/vnd.ms-excel",
        headers={
            "Content-Disposition": f"attachment; filename=attendance_{user['username']}.xls"
        },
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False,
    )
