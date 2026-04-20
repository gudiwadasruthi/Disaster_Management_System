# create_admin.py - Run this in backend folder
import sqlite3
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash the password admin1234
hashed = pwd_context.hash("admin1234")

conn = sqlite3.connect('disaster.db')
cursor = conn.cursor()

# Check if admin already exists
cursor.execute("SELECT id FROM users WHERE email = 'admin@test.com'")
existing = cursor.fetchone()

if existing:
    print("Admin already exists. Updating password...")
    cursor.execute("""
        UPDATE users 
        SET hashed_password = ? 
        WHERE email = 'admin@test.com'
    """, (hashed,))
else:
    print("Creating new admin...")
    cursor.execute("""
        INSERT INTO users (full_name, email, phone_number, hashed_password, city, role)
        VALUES ('Admin User', 'admin@test.com', '7777777777', ?, 'Hyderabad', 'ADMIN')
    """, (hashed,))

conn.commit()
conn.close()
print("Admin ready: admin@test.com / admin1234")