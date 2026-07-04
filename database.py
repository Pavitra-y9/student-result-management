import os
import sqlite3
from werkzeug.security import generate_password_hash

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')

def get_db_connection():
    """Establishes a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")  # Ensure foreign key constraints are enforced
    return conn

def init_db():
    """Initializes the database schema and inserts a default admin if none exists."""
    # Read schema
    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Execute the schema script
    cursor.executescript(schema_sql)
    
    # Create default admin user
    admin_username = 'admin'
    admin_password_hash = generate_password_hash('admin123')
    
    # Check if admin already exists (shouldn't since schema drops tables, but good practice)
    cursor.execute("SELECT * FROM users WHERE username = ?", (admin_username,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (admin_username, admin_password_hash, 'admin')
        )
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
