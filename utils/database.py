"""
Database utilities for YBB Data Management API
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection and query management"""
    
    def __init__(self):
        self.engine = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize database connection"""
        try:
            db_host = os.getenv('DB_HOST', 'localhost')
            db_user = os.getenv('DB_USER', 'root')
            db_password = os.getenv('DB_PASSWORD', '')
            db_name = os.getenv('DB_NAME', 'ybb_data_management')
            db_port = os.getenv('DB_PORT', '3306')
            
            database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            self.engine = create_engine(database_url, echo=False)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Database connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {str(e)}")
            self.engine = None
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        if not self.engine:
            raise Exception("Database connection not available")
        
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), params or {})
                return result.fetchall(), list(result.keys())
        except SQLAlchemyError as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise Exception(f"Query failed: {str(e)}")
    
    def test_connection(self):
        """Test database connection"""
        try:
            if not self.engine:
                return False
            
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
