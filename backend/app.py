import os
import time
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "appdb"),
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD", "apppass"),
    )

def init_db():
    # simple retry (useful in docker/k8s when db isn't ready yet)
    for _ in range(30):
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS items (
                            id SERIAL PRIMARY KEY,
                            text TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("DB not ready after retries")

@app.route("/api/items", methods=["GET"])
def list_items():
    init_db()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, text, created_at FROM items ORDER BY created_at DESC")
            rows = cur.fetchall()
    return jsonify([
        {"id": r[0], "text": r[1], "created_at": r[2].isoformat()}
        for r in rows
    ])

@app.route("/api/items", methods=["POST"])
def create_item():
    init_db()
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return {"error": "text is required"}, 400

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO items (text) VALUES (%s)", (text,))
    return {"status": "ok"}, 201