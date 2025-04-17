import sqlite3
import os

class DatabaseConfig:
    def __init__(self):
        # Create data directory if it doesn't exist
        # This directory will store the SQLite database file
        if not os.path.exists("data"):
            os.makedirs("data")
        
        # Set the path for the SQLite database file
        # The database will be stored in the data folder as passwords.db
        self.db_path = os.path.join("data", "passwords.db")
        self.init_database()

    def init_database(self):
        # Get a connection to the database
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create the passwords table if it doesn't exist
        # The table stores:
        # - id: Auto-incrementing primary key
        # - website: Website name (required)
        # - email: Email address (optional)
        # - password: Password (required)
        # - notes: Additional notes (optional)
        # - created_at: Timestamp when entry was created
        # - updated_at: Timestamp when entry was last modified
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website TEXT NOT NULL,
                email TEXT,
                password TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Save changes and close the connection
        conn.commit()
        conn.close()

    def get_connection(self):
        # Return a new connection to the SQLite database
        return sqlite3.connect(self.db_path) 