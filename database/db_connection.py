"""
Database Connection Manager for YBB Data Management Service
Handles secure database connections with connection pooling
"""
import os
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import pandas as pd
from config import get_config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections with pooling and security"""
    
    def __init__(self):
        self.config = get_config()
        self.engine = None
        self.Session = None
        self._init_connection()
    
    def _init_connection(self):
        """Initialize database connection with pooling"""
        try:
            # Get database configuration from environment
            db_config = {
                'host': os.environ.get('DB_HOST', 'localhost'),
                'port': int(os.environ.get('DB_PORT', 3306)),
                'user': os.environ.get('DB_USER', 'root'),
                'password': os.environ.get('DB_PASSWORD', ''),
                'database': os.environ.get('DB_NAME', 'ybb_data_management'),
                'charset': 'utf8mb4'
            }
            
            # Create connection string
            connection_string = (
                f"mysql+pymysql://{db_config['user']}:{db_config['password']}@"
                f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
                f"?charset={db_config['charset']}"
            )
            
            # Create engine with connection pooling
            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=5,          # Number of connections to maintain
                max_overflow=10,      # Additional connections allowed
                pool_timeout=30,      # Timeout for getting connection
                pool_recycle=3600,    # Recycle connections after 1 hour
                echo=self.config.DEBUG  # Log SQL queries in debug mode
            )
            
            # Create session factory
            self.Session = sessionmaker(bind=self.engine)
            
            # Test connection
            self._test_connection()
            
            logger.info("✅ Database connection initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database connection: {e}")
            raise
    
    def _test_connection(self):
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                test_value = result.fetchone()[0]
                if test_value != 1:
                    raise Exception("Connection test failed")
                logger.info("✅ Database connection test passed")
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection context manager"""
        connection = None
        try:
            connection = self.engine.connect()
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if connection:
                try:
                    connection.rollback()
                except:
                    pass  # Ignore rollback errors
            raise
        finally:
            if connection:
                try:
                    connection.close()
                except:
                    pass  # Ignore close errors
    
    @contextmanager
    def get_session(self):
        """Get database session context manager"""
        session = None
        try:
            session = self.Session()
            yield session
            session.commit()
        except Exception as e:
            logger.error(f"Database session error: {e}")
            if session:
                session.rollback()
            raise
        finally:
            if session:
                session.close()
    
    def execute_query_to_dataframe(self, query, params=None, chunk_size=None):
        """
        Execute query and return pandas DataFrame
        Supports chunked reading for large datasets
        """
        try:
            with self.get_connection() as conn:
                if chunk_size:
                    # Read in chunks for large datasets
                    chunks = []
                    for chunk in pd.read_sql(query, conn, params=params, chunksize=chunk_size):
                        chunks.append(chunk)
                    return pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()
                else:
                    # Read entire result set
                    return pd.read_sql(query, conn, params=params)
                    
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise
    
    def execute_query_chunked(self, query, params=None, chunk_size=5000):
        """
        Execute query and yield chunks for memory-efficient processing
        Generator function for very large datasets
        """
        try:
            with self.get_connection() as conn:
                for chunk in pd.read_sql(query, conn, params=params, chunksize=chunk_size):
                    yield chunk
        except Exception as e:
            logger.error(f"Chunked query execution error: {e}")
            raise
    
    def get_record_count(self, table_name, where_clause="", params=None):
        """Get total record count for a table/query"""
        try:
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            if where_clause:
                count_query += f" WHERE {where_clause}"
            
            with self.get_connection() as conn:
                result = conn.execute(text(count_query), params or {})
                return result.fetchone()[0]
        except Exception as e:
            logger.error(f"Count query error: {e}")
            raise

# Global database manager instance (lazy initialization)
_db_manager = None

def get_db_manager():
    """Get or create database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

# Convenience functions
def get_db_connection():
    """Get database connection context manager"""
    return get_db_manager().get_connection()

def get_db_session():
    """Get database session context manager"""
    return get_db_manager().get_session()

def execute_query(query, params=None, chunk_size=None):
    """Execute query and return DataFrame"""
    return get_db_manager().execute_query_to_dataframe(query, params, chunk_size)

def execute_chunked_query(query, params=None, chunk_size=5000):
    """Execute query in chunks (generator)"""
    return get_db_manager().execute_query_chunked(query, params, chunk_size)

def get_table_count(table_name, where_clause="", params=None):
    """Get record count"""
    return get_db_manager().get_record_count(table_name, where_clause, params)