import hashlib
import psycopg2
import time

# Database connection settings
DB1_CONFIG = {
    "dbname": "db1",
    "user": "user1",
    "password": "password1",
    "host": "localhost",
    "port": "5432",
}

DB2_CONFIG = {
    "dbname": "db2",
    "user": "user2",
    "password": "password2",
    "host": "localhost",
    "port": "5433",
}

def connect_db(config):
    """Connect to PostgreSQL database."""
    return psycopg2.connect(**config)

def get_table_hash(cursor, table_name):
    """Compute a hashset of the entire table to verify row integrity."""
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY id;")  # Ensuring consistent order
    rows = cursor.fetchall()
    
    # Convert each row to a hashable string and compute a cumulative hash
    hash_obj = hashlib.sha256()
    for row in rows:
        hash_obj.update(str(row).encode())  # Encoding to bytes
    
    return hash_obj.hexdigest()  # Return unique hash of the table

def verify_sync():
    """Step 1: Verify row count, Step 2: Verify hash of both tables."""
    
    conn1 = connect_db(DB1_CONFIG)
    conn2 = connect_db(DB2_CONFIG)
    cursor1 = conn1.cursor()
    cursor2 = conn2.cursor()

    # Step 1: Verify row count
    cursor1.execute("SELECT COUNT(*) FROM users;")
    count1 = cursor1.fetchone()[0]

    cursor2.execute("SELECT COUNT(*) FROM users;")
    count2 = cursor2.fetchone()[0]

    if count1 == count2:
        print(f"[✓] Row count matches: {count1} rows in both db1 and db2")
    else:
        print(f"[!] Row count mismatch: db1 has {count1}, db2 has {count2}")

    # Step 2: Verify data integrity using hash comparison
    hash1 = get_table_hash(cursor1, "users")
    hash2 = get_table_hash(cursor2, "users")

    if hash1 == hash2:
        print("[✓] Hash verification successful: Both tables have identical data")
    else:
        print("[!] Hash mismatch: Data in db1 and db2 are different")

    # Close connections
    cursor1.close()
    cursor2.close()
    conn1.close()
    conn2.close()

# Run verification
verify_sync()
