"""
Database module for airline discount ML project.
Uses SQLite for simplicity in training environments.
"""
import sqlite3
import os
from pathlib import Path


class Database:
    """Database connection and operations handler."""
    
    def __init__(self, db_path=None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Store database in project root
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / 'data' / 'airline_discount.db'
        
        self.db_path = str(db_path)
        self.connection = None

    def connect(self):
        """Establish database connection."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            print(f"✓ Database connection successful: {self.db_path}")
            return self.connection
        except Exception as e:
            print(f"✗ Error connecting to database: {e}")
            return None

    def fetch_data(self, query, params=None):
        """
        Execute a SELECT query and fetch results.
        
        Args:
            query: SQL query string
            params: Optional parameters for the query
            
        Returns:
            List of rows or None if error
        """
        if self.connection is None:
            print("Database not connected. Please connect first.")
            return None
        
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
        finally:
            cursor.close()

    def execute(self, query, params=None):
        """
        Execute a query (INSERT, UPDATE, DELETE).
        
        Args:
            query: SQL query string
            params: Optional parameters for the query
            
        Returns:
            True if successful, False otherwise
        """
        if self.connection is None:
            print("Database not connected. Please connect first.")
            return False
        
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error executing query: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None


def init_database(db_path=None):
    """
    Initialize the database with the schema.
    Creates tables if they don't exist.
    
    Args:
        db_path: Optional path to database file
    """
    print("Initializing database...")
    
    # Get schema file path
    project_root = Path(__file__).parent.parent.parent
    schema_file = project_root / 'data' / 'schema.sql'
    
    if not schema_file.exists():
        print(f"✗ Schema file not found: {schema_file}")
        return False
    
    # Read schema from file
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema = f.read()
    except Exception as e:
        print(f"✗ Error reading schema file: {e}")
        return False
    
    # Create database and tables
    db = Database(db_path)
    db.connect()
    
    try:
        # Execute schema
        cursor = db.connection.cursor()
        cursor.executescript(schema)
        db.connection.commit()
        print("✓ Database tables created successfully")
        
        # Load sample data if available
        sample_data_file = project_root / 'data' / 'sample_data.sql'
        if sample_data_file.exists():
            load_sample_data_from_file(db, sample_data_file)
        
        return True
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        return False
    finally:
        db.close()


def load_sample_data_from_file(db, sample_data_file):
    """
    Load sample data from SQL file.
    
    Args:
        db: Database instance
        sample_data_file: Path to sample data SQL file
    """
    print("Loading sample data from file...")
    
    try:
        with open(sample_data_file, 'r', encoding='utf-8') as f:
            sample_data_sql = f.read()
        
        cursor = db.connection.cursor()
        cursor.executescript(sample_data_sql)
        db.connection.commit()
        print("✓ Sample data loaded successfully from file")
        return True
        
    except Exception as e:
        print(f"✗ Error loading sample data from file: {e}")
        return False


def load_sample_data(db=None):
    """
    Load sample data into the database.
    
    Args:
        db: Database instance (optional)
    """
    print("Loading sample data...")
    
    close_after = False
    if db is None:
        db = Database()
        db.connect()
        close_after = True
    
    try:
        # Sample passengers
        passengers = [
            ("John Smith", '{"flights": 10, "miles": 5000}'),
            ("Jane Doe", '{"flights": 25, "miles": 15000}'),
            ("Bob Johnson", '{"flights": 5, "miles": 2500}'),
        ]
        
        cursor = db.connection.cursor()
        cursor.executemany(
            "INSERT INTO passengers (name, travel_history) VALUES (?, ?)",
            passengers
        )
        
        # Sample routes
        routes = [
            ("New York", "London", 3459.0),
            ("Los Angeles", "Tokyo", 5478.0),
            ("San Francisco", "Paris", 5558.0),
        ]
        
        cursor.executemany(
            "INSERT INTO routes (origin, destination, distance) VALUES (?, ?, ?)",
            routes
        )
        
        # Sample discounts
        discounts = [
            (1, 1, 15.0),
            (2, 2, 25.0),
            (3, 3, 10.0),
        ]
        
        cursor.executemany(
            "INSERT INTO discounts (passenger_id, route_id, discount_value) VALUES (?, ?, ?)",
            discounts
        )
        
        db.connection.commit()
        print("✓ Sample data loaded successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error loading sample data: {e}")
        return False
    finally:
        if close_after:
            db.close()


def get_connection():
    """
    Get a database connection (convenience function).
    
    Returns:
        Database instance
    """
    db = Database()
    db.connect()
    return db