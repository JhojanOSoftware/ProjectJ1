"""Database connection management."""
import os
import pymysql
from contextlib import contextmanager
from typing import Generator
import logging

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration from environment variables."""
    
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.user = os.getenv("DB_USER", "jhojan")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME", "J_Arrendatarios")
        self.charset = "utf8mb4"
    
    def to_dict(self) -> dict:
        """Convert to pymysql connection dictionary."""
        return {
            "host": self.host,
            "user": self.user,
            "password": self.password,
            "database": self.database,
            "charset": self.charset,
            "cursorclass": pymysql.cursors.DictCursor
        }


class DatabaseConnection:
    """Manages database connections with context manager support."""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
    
    def connect(self):
        """Create a new database connection."""
        try:
            conn = pymysql.connect(**self.config.to_dict())
            logger.debug(f"Connected to {self.config.database}@{self.config.host}")
            return conn
        except pymysql.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    @contextmanager
    def get_connection(self) -> Generator:
        """Context manager for database connections."""
        conn = None
        try:
            conn = self.connect()
            yield conn
        finally:
            if conn:
                conn.close()
                logger.debug("Connection closed")


# Singleton instance
_db = DatabaseConnection()


def get_connection():
    """Get a database connection (legacy support)."""
    return _db.connect()


@contextmanager
def get_db_context():
    """Get a context-managed database connection."""
    with _db.get_connection() as conn:
        yield conn
