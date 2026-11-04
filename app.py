import sqlite3

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.get("/users")
def users():
    name = request.args.get("name", "")
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    # SQL injection: user input concatenated straight into the query.
    query = f"SELECT id, name FROM users WHERE name = '{name}'"
    rows = cur.execute(query).fetchall()
    return jsonify(rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
