# =====================================================================
# FILE: database_server.py
# Purpose: SQLite Connection Pooling, Persistence & Flask 24/7 Server
# =====================================================================

import sqlite3
import threading
import os
from typing import List
from flask import Flask, jsonify, render_template_string
from config import DATABASE_FILENAME, DEFAULT_PORT, BOT_VERSION, LOGGER

# --- THREAD-SAFE DATABASE MANAGER ---
DATABASE_LOCK = threading.Lock()

class MassiveDatabaseManager:
    """Manages heavy database queries, group storage, and analytics safely."""
    
    def __init__(self, db_path: str = DATABASE_FILENAME) -> None:
        self.db_path = db_path
        self._initialize_heavy_database()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=60.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_heavy_database(self) -> None:
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
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS message_logs (
                            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            message_text TEXT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    conn.commit()
                    LOGGER.info("Heavy enterprise database tables successfully verified/created.")
            except Exception as exc:
                LOGGER.critical(f"Database initialization failure: {exc}")

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
                    cursor.execute('SELECT chat_id FROM enterprise_groups')
                    return [row['chat_id'] for row in cursor.fetchall()]
            except Exception as exc:
                LOGGER.error(f"Error fetching all group IDs: {exc}")
                return []

    def log_incoming_message(self, user_id: int, text: str) -> None:
        with DATABASE_LOCK:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        'INSERT INTO message_logs (user_id, message_text) VALUES (?, ?)',
                        (user_id, text[:255])
                    )
                    conn.commit()
            except Exception as exc:
                LOGGER.error(f"Error logging message: {exc}")

DB_INSTANCE = MassiveDatabaseManager()

# --- 24/7 FLASK UPTIME WEB SERVER ---
class MassiveUptimeServer:
    
    def __init__(self, port: int = DEFAULT_PORT) -> None:
        self.port = port
        self.server_app = Flask("MassiveEnterpriseServer")
        self._configure_endpoints()

    def _configure_endpoints(self) -> None:
        @self.server_app.route('/')
        def render_home():
            return render_template_string("""
                <html>
                <body style="background:#090d16; color:#f1f5f9; font-family:sans-serif; text-align:center; padding-top:60px;">
                    <div style="background:#1e293b; max-width:650px; margin:0 auto; padding:40px; border-radius:15px; box-shadow:0 15px 30px rgba(0,0,0,0.5);">
                        <h1 style="color:#38bdf8;">Massive Enterprise Bot 10M+ 🚀</h1>
                        <p>Status: <span style="background:#22c55e; padding:5px 12px; border-radius:20px; font-weight:bold;">ONLINE 24/7</span></p>
                        <p>Version: {{ version }}</p>
                    </div>
                </body>
                </html>
            """, version=BOT_VERSION)

        @self.server_app.route('/health')
        def health_check():
            return jsonify({"status": "healthy", "version": BOT_VERSION}), 200

    def start_server_process(self) -> None:
        try:
            self.server_app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
        except Exception as exc:
            LOGGER.critical(f"Uptime server startup error: {exc}")

    def spawn_server_thread(self) -> None:
        server_thread = threading.Thread(target=self.start_server_process, daemon=True, name="HeavyWebServerThread")
        server_thread.start()
        LOGGER.info("Massive uptime web server successfully spawned in background thread.")

WEB_SERVER_INSTANCE = MassiveUptimeServer()
              
