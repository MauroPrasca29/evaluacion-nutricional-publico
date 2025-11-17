"""Reset admin password directly using SQL."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from passlib.context import CryptContext
import psycopg2

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def reset_admin_password():
    # Database connection
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:VJjfJIAOHZHiDfiKlRdoymRRZVkPeIvW@junction.proxy.rlwy.net:17565/railway")
    
    # Parse connection string
    # postgresql://user:pass@host:port/dbname
    parts = db_url.replace("postgresql://", "").split("@")
    user_pass = parts[0].split(":")
    host_port_db = parts[1].split("/")
    host_port = host_port_db[0].split(":")
    
    user = user_pass[0]
    password = user_pass[1]
    host = host_port[0]
    port = host_port[1]
    dbname = host_port_db[1]
    
    # Admin password
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    hashed_password = pwd_context.hash(admin_password)
    
    print(f"Connecting to {host}:{port}/{dbname}...")
    print(f"New hashed password for admin123: {hashed_password}")
    
    # Connect and update
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        connect_timeout=10
    )
    
    try:
        cursor = conn.cursor()
        
        # Update admin password
        cursor.execute(
            "UPDATE usuarios SET contrasena = %s WHERE correo = %s",
            (hashed_password, "admin@example.com")
        )
        
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Successfully updated password for admin@example.com")
            print(f"   You can now login with:")
            print(f"   Email: admin@example.com")
            print(f"   Password: {admin_password}")
        else:
            print("❌ No user found with email admin@example.com")
        
        cursor.close()
    finally:
        conn.close()


if __name__ == "__main__":
    reset_admin_password()
