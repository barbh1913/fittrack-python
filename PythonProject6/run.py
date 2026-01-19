"""
Flask Application Entry Point
Run this file to start the gym management API server
"""
import logging
import os
from backend.app.app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    app = create_app()
    
    # Test database connection on startup
    from backend.app.repositories.db_manager import SQLManger
    from backend.app.models import Base
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.ini")
    db_manager = SQLManger(config_path=config_path)
    
    if db_manager.test_connection():
        print("✅ Database connection successful!")
        
        # Create tables if they don't exist
        try:
            print("📋 Checking database tables...")
            Base.metadata.create_all(db_manager.engine)
            print("✅ Database tables ready")
        except Exception as e:
            print(f"⚠️  Warning: Could not create tables: {e}")
            print("   You may need to run 'python seed.py' to create tables and load data")
        
        print("🚀 Starting Flask server on http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Database connection failed! Please check your config.ini")
        exit(1)
