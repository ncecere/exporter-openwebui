import psycopg2
from psycopg2 import pool
import logging
from config import (
    DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT,
    DB_MIN_CONNECTIONS, DB_MAX_CONNECTIONS
)

logger = logging.getLogger(__name__)

class DatabasePool:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabasePool, cls).__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance

    def _initialize_pool(self):
        """Initialize the connection pool"""
        try:
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=DB_MIN_CONNECTIONS,
                maxconn=DB_MAX_CONNECTIONS,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            logger.info(f"Initialized DB connection pool (min={DB_MIN_CONNECTIONS}, max={DB_MAX_CONNECTIONS})")
        except Exception as e:
            logger.error(f"Error initializing connection pool: {e}")
            raise

    def get_connection(self):
        """Get a connection from the pool"""
        return DatabaseConnection(self)

    def _get_raw_connection(self):
        """Internal method to get a raw connection from the pool"""
        try:
            return self.pool.getconn()
        except Exception as e:
            logger.error(f"Error getting connection from pool: {e}")
            raise

    def _return_connection(self, conn):
        """Internal method to return a connection to the pool"""
        try:
            self.pool.putconn(conn)
        except Exception as e:
            logger.error(f"Error returning connection to pool: {e}")
            raise

    def close_all(self):
        """Close all connections in the pool"""
        try:
            self.pool.closeall()
            logger.info("Closed all database connections")
        except Exception as e:
            logger.error(f"Error closing connection pool: {e}")
            raise

class DatabaseConnection:
    """Context manager for database connections"""

    def __init__(self, pool):
        self.pool = pool
        self.conn = None
        self._cursor = None

    def __enter__(self):
        self.conn = self.pool._get_raw_connection()
        self._cursor = self.conn.cursor()
        return self._cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._cursor is not None:
            self._cursor.close()
        if self.conn is not None:
            if exc_type is not None:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.pool._return_connection(self.conn)

def get_db_pool():
    """Get the database connection pool singleton"""
    return DatabasePool()
