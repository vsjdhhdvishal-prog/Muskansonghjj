# =====================================================================
# FILE: database_server.py (With Default Group Auto-Fix)
# =====================================================================

import sqlite3
import threading
import os
from typing import List
from flask import Flask, jsonify, render_template_string
from config import DATABASE_FILENAME, DEFAULT_PORT, BOT_VERSION, LOGGER

DATABASE_LOCK = threading.Lock()

class MassiveDatabaseManager:
    def __init__(self, db_path: str = DATABASE_FILENAME) -> None:
        self.db_path = db_path
        self._initialize_database()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=60.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_database(self) -> None:
        with DATABASE_LOCK:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS enterprise_groups (
                            chat_id INTEGER PRIMARY KEY,
                            title TEXT NOT NULL,
                            registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    # Safety check: Agar database bilkul khali hai toh ek default placeholder daal do taaki error na aaye
                    cursor.execute('SELECT COUNT(*) as cnt FROM enterprise_groups')
                    row = cursor.fetchone()
                    if row and row['cnt'] == 0:
                        cursor.execute(
                            'INSERT OR IGNORE INTO enterprise_groups (chat_id, title) VALUES (?, ?)',
                            (-100123456789, "Default Enterprise Group")
                        )
                    conn.commit()
                    LOGGER.info("Database initialized successfully with safety check.")
            except Exception as exc:
                LOGGER.critical(f"Database init error: {exc}")

    def add_group(self, chat_id: int, title: str) -> None:
        with DATABASE_LOCK:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        'INSERT OR IGNORE INTO enterprise_groups (chat_id, title) VALUES (?, ?)',
                        (chat_id, title)
                    )
                    conn.commit()
            except Exception as exc:
                LOGGER.error(f"Error adding group {chat_id}: {exc}")

    def remove_group(self, chat_id: int) -> None:
        with DATABASE_LOCK:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM enterprise_groups WHERE chat_id = ?', (chat_id,))
                    conn.commit()
            except Exception as exc:
                LOGGER.error(f"Error removing group {chat_id}: {exc}")

    def fetch_all_groups(self) -> List[int]:
        with DATABASE_LOCK:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    # Sirf valid real group IDs return karenge (default placeholder ko hata kar)
                    cursor.execute('SELECT chat_id FROM enterprise_groups WHERE chat_id != -100123456789')
                    return [row['chat_id'] for row in cursor.fetchall()]
            except Exception as exc:
                LOGGER.error(f"Error fetching groups: {exc}")
                return []

DB_INSTANCE = MassiveDatabaseManager()

class MassiveUptimeServer:
    def __init__(self, port: int = DEFAULT_PORT) -> None:
        self.port = port
        self.server_app = Flask("EnterpriseServer")
        self._configure_endpoints()

    def _configure_endpoints(self) -> None:
        @self.server_app.route('/')
        def render_home():
            return render_template_string("""
                <html>
                <body style="background:#090d16; color:#f1f5f9; text-align:center; padding-top:60px;">
                    <h1 style="color:#38bdf8;">Enterprise Bot Online 🚀</h1>
                    <p>Status: <b>ONLINE 24/7</b> | Version: {{ version }}</p>
                </body>
                </html>
            """, version=BOT_VERSION)

        @self.server_app.route('/health')
        def health_check():
            return jsonify({"status": "healthy", "version": BOT_VERSION}), 200

    def spawn_server_thread(self) -> None:
        threading.Thread(
            target=lambda: self.server_app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False),
            daemon=True,
            name="WebServerThread"
        ).start()
        LOGGER.info("Uptime web server spawned.")

WEB_SERVER_INSTANCE = MassiveUptimeServer()
