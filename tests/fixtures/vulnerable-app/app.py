"""Intentionally vulnerable Flask-style app. FIXTURE ONLY: never deploy or run."""

import sqlite3
import subprocess

from flask import Flask, request, send_file

app = Flask(__name__)

# SEEDED VULN 1 (CWE-798): hardcoded credential. The value is obviously fake.
API_KEY = "FAKE-NOT-A-REAL-KEY-0000"

UPLOAD_DIR = "/srv/uploads"


def db():
    return sqlite3.connect("app.db")


@app.route("/user")
def get_user_by_name():
    name = request.args["name"]
    # SEEDED VULN 2 (CWE-89): SQL injection, user input concatenated into the query.
    row = db().execute("SELECT * FROM users WHERE name = '" + name + "'").fetchone()
    return str(row)


@app.route("/ping")
def ping():
    host = request.args["host"]
    # SEEDED VULN 3 (CWE-78): command injection, user input reaches a shell.
    out = subprocess.run("ping -c 1 " + host, shell=True, capture_output=True)
    return out.stdout


@app.route("/download")
def download():
    filename = request.args["file"]
    # SEEDED VULN 4 (CWE-22): path traversal, "../" in filename escapes UPLOAD_DIR.
    return send_file(UPLOAD_DIR + "/" + filename)


@app.route("/invoice/<int:invoice_id>")
def invoice(invoice_id):
    # SEEDED VULN 5 (CWE-639): IDOR. No check that the invoice belongs to the caller.
    row = db().execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    return str(row)
