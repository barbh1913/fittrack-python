import os

from flask import Flask
from flask_cors import CORS

from backend.app.repositories.db_manager import SQLManger
from backend.app.api.checkin_api import create_checkin_blueprint
from backend.app.api.class_sessions import create_sessions_blueprint
from backend.app.api.members_api import create_members_blueprint
from backend.app.api.trainers_api import create_trainers_blueprint
from backend.app.api.admins_api import create_admins_blueprint
from backend.app.api.waiting_list_api import create_waiting_list_blueprint
from backend.app.api.progress_api import create_progress_blueprint
from backend.app.api.financial_api import create_financial_blueprint
from backend.app.exceptions.handlers import register_error_handlers


def create_app():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "..", "..", "config.ini")
    static_folder = os.path.join(base_dir, "..", "..", "frontend", "static")

    db_manager = SQLManger(config_path=config_path)

    # Check if React build exists, otherwise serve development files
    react_build = os.path.join(static_folder, 'dist')
    if os.path.exists(react_build):
        app = Flask(__name__, static_folder=react_build, static_url_path='')
    else:
        app = Flask(__name__, static_folder=static_folder, static_url_path='')
    
    # Enable CORS for React app
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    register_error_handlers(app)

    # Register all API blueprints FIRST (before catch-all route)
    from backend.app.api.subscriptions_api import create_subscriptions_blueprint
    from backend.app.api.workout_plans_api import create_workout_plans_blueprint
    
    app.register_blueprint(create_members_blueprint(db_manager))  # Member endpoints
    app.register_blueprint(create_trainers_blueprint(db_manager))  # Trainer endpoints
    app.register_blueprint(create_admins_blueprint(db_manager))  # Admin endpoints
    app.register_blueprint(create_subscriptions_blueprint(db_manager))
    app.register_blueprint(create_sessions_blueprint(db_manager))
    app.register_blueprint(create_workout_plans_blueprint(db_manager))
    app.register_blueprint(create_checkin_blueprint(db_manager))
    app.register_blueprint(create_waiting_list_blueprint(db_manager))  # NEW: Waiting list
    app.register_blueprint(create_progress_blueprint(db_manager))  # NEW: Progress tracking
    app.register_blueprint(create_financial_blueprint(db_manager))  # NEW: Financial reports
    
    # Register catch-all route LAST (for React Router)
    @app.route('/')
    def index():
        """Serve the main UI page."""
        return app.send_static_file('index.html')
    
    # Catch-all for React Router (must be last)
    @app.route('/<path:path>')
    def serve_react(path):
        """Serve React app for all non-API routes."""
        # Don't serve HTML for API routes - return JSON 404
        if path.startswith('api/'):
            from flask import jsonify
            return jsonify({
                "http": {
                    "code": 404,
                    "name": "NOT_FOUND",
                    "message": "Not Found"
                },
                "success": False,
                "error": "API endpoint not found",
                "path": path
            }), 404
        # For all other paths, serve React app (for client-side routing)
        try:
            return app.send_static_file('index.html')
        except:
            from flask import jsonify
            return jsonify({"error": "File not found"}), 404

    return app
