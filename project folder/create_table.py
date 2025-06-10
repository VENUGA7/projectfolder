import sqlite3

# Create or connect to database
conn = sqlite3.connect('database.db')

# Create table if not exists
conn.execute('''
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    expiry TEXT,
    price TEXT,
    image TEXT
)
''')

# Close the connection
conn.close()

print("Database created and table created successfully!")
