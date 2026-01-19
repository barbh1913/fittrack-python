"""
Database connection manager - handles MySQL connection and session creation.
"""
from configparser import ConfigParser
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

class SQLManger:
    """
    SQL Manager - manages database connections and provides session factory.
    Reads configuration from config.ini file.
    """
    def __init__(self, config_path="config.ini", section="mysql"):
        self.config = ConfigParser()

        # Try to find config file (check relative path first, then project root)
        config_file = Path(config_path)
        if not config_file.is_file():
            config_file = Path(__file__).parent.parent.parent.parent / config_path

        self.config.read(config_file)

        # Read database configuration
        db = self.config[section]
        self.host = db["host"]
        self.port = db.get("port", "3306")
        self.user = db["user"]
        self.password = db["password"]
        self.dbname = db["database"]

        # Engine to MySQL server (no specific database selected - for creating DB)
        self.server_url = f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/"
        self.server_engine = create_engine(self.server_url, future=True)

        # Engine to specific database (for normal operations)
        self.db_url = f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
        self.engine = create_engine(self.db_url, future=True)

        # Session factory - creates database sessions for repositories
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, future=True)

    def test_connection(self):
        """Test database connection and create database if it doesn't exist."""
        try:
            with self.server_engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{self.dbname}`;"))
                conn.commit()
            return True
        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ Connection failed: {error_msg}")
            
            # Provide helpful error messages
            if "Access denied" in error_msg or "1045" in error_msg:
                print("   → Check your username and password in config.ini")
                print(f"   → Current user: {self.user}")
                print("   → Make sure the password matches your MySQL root password")
            elif "Can't connect" in error_msg or "2003" in error_msg:
                print("   → Make sure MySQL server is running")
                print(f"   → Check if MySQL is accessible at {self.host}:{self.port}")
                print("   → Start MySQL service if it's not running")
            elif "No module named 'pymysql'" in error_msg:
                print("   → Install pymysql: py -m pip install pymysql")
            else:
                print(f"   → Error type: {type(e).__name__}")
            return False
