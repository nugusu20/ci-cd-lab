from datetime import datetime, UTC
from flask import Flask, jsonify, request

from app.db import get_connection, init_db

app = Flask(__name__)
init_db()


def now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def row_to_task(row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@app.get("/health")
def health() -> tuple:
    return jsonify({"status": "ok"}), 200


@app.get("/tasks")
def list_tasks() -> tuple:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM tasks ORDER BY id DESC"
        ).fetchall()

    return jsonify([row_to_task(row) for row in rows]), 200


@app.post("/tasks")
def create_task() -> tuple:
    payload = request.get_json(silent=True) or {}

    title = str(payload.get("title", "")).strip()
    description = str(payload.get("description", "")).strip()

    if not title:
        return jsonify({"error": "title is required"}), 400

    timestamp = now_iso()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (title, description, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, description, "todo", timestamp, timestamp),
        )
        task_id = cursor.lastrowid
        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        connection.commit()

    return jsonify(row_to_task(row)), 201


@app.get("/tasks/<int:task_id>")
def get_task(task_id: int) -> tuple:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    if row is None:
        return jsonify({"error": "task not found"}), 404

    return jsonify(row_to_task(row)), 200


@app.patch("/tasks/<int:task_id>")
def update_task(task_id: int) -> tuple:
    payload = request.get_json(silent=True) or {}

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        if existing is None:
            return jsonify({"error": "task not found"}), 404

        title = str(payload.get("title", existing["title"])).strip()
        description = str(payload.get("description", existing["description"])).strip()
        status = str(payload.get("status", existing["status"])).strip()

        if not title:
            return jsonify({"error": "title is required"}), 400

        if status not in {"todo", "doing", "done"}:
            return jsonify({"error": "status must be one of: todo, doing, done"}), 400

        updated_at = now_iso()

        connection.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, status = ?, updated_at = ?
            WHERE id = ?
            """,
            (title, description, status, updated_at, task_id),
        )

        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        connection.commit()

    return jsonify(row_to_task(row)), 200


@app.delete("/tasks/<int:task_id>")
def delete_task(task_id: int) -> tuple:
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        if existing is None:
            return jsonify({"error": "task not found"}), 404

        connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        connection.commit()

    return jsonify({"deleted": True, "id": task_id}), 200


@app.get("/stats")
def stats() -> tuple:
    with get_connection() as connection:
        total = connection.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        todo = connection.execute(
            "SELECT COUNT(*) FROM tasks WHERE status = 'todo'"
        ).fetchone()[0]
        doing = connection.execute(
            "SELECT COUNT(*) FROM tasks WHERE status = 'doing'"
        ).fetchone()[0]
        done = connection.execute(
            "SELECT COUNT(*) FROM tasks WHERE status = 'done'"
        ).fetchone()[0]

    return jsonify(
        {
            "total": total,
            "todo": todo,
            "doing": doing,
            "done": done,
        }
    ), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
