# =====================================================================
# FILE 3 OF 5: server.py (Updated)
# Purpose: Flask Health Check and 24/7 Uptime Web Server
# =====================================================================

import os
import threading
from flask import Flask, jsonify, render_template_string
from config import DEFAULT_PORT, LOGGER, BOT_VERSION

class EnterpriseWebServer:
    """Handles HTTP health checks and keeps cloud instances awake 24/7."""
    
    def __init__(self, port: int = DEFAULT_PORT) -> None:
        self.port = port
        self.app = Flask("EnterpriseUptimeServer")
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Registers web endpoints for status monitoring."""
        
        @self.app.route('/')
        def index():
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Telegram Bot - Enterprise Status</title>
                <style>
                    body { font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; text-align: center; padding-top: 50px; }
                    .card { background: #1e293b; max-width: 600px; margin: 0 auto; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
                    h1 { color: #38bdf8; }
                    .badge { background: #22c55e; color: white; padding: 6px 12px; border-radius: 20px; font-weight: bold; }
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>Enterprise Bot Online</h1>
                    <p>Status: <span class="badge">ACTIVE 24/7</span></p>
                    <p>Version: {{ version }}</p>
                    <p>Architecture: Modular 5-Part Enterprise Engine</p>
                </div>
            </body>
            </html>
            """
            return render_template_string(html_template, version=BOT_VERSION)

        @self.app.route('/health')
        def health_check():
            """JSON health endpoint for automated ping monitors."""
            LOGGER.debug("Health check ping received via HTTP.")
            return jsonify({
                "status": "healthy",
                "service": "telegram-bot-worker",
                "version": BOT_VERSION
            }), 200

    def run_server(self) -> None:
        """Starts the Flask server bound to all network interfaces."""
        try:
            LOGGER.info(f"Starting uptime web server on port {self.port}...")
            self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
        except Exception as exc:
            LOGGER.critical(f"Failed to start web server: {exc}")

    def start_background_thread(self) -> threading.Thread:
        """Launches the web server in a separate background daemon thread."""
        server_thread = threading.Thread(target=self.run_server, daemon=True, name="UptimeServerThread")
        server_thread.start()
        LOGGER.info("Uptime web server successfully spawned in background thread.")
        return server_thread

WEB_SERVER = EnterpriseWebServer()
