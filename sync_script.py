import hashlib
import psycopg2
import time

# Database connection settings
DB1_CONFIG = {
    "dbname": "db1",
    "user": "user1",
    "password": "password1",
    "host": "localhost",  # Use 'localhost' outside Docker
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
    #Connect to PostgreSQL database
    return psycopg2.connect(**config)

def insert_data():
    #Insert 100 rows into db1
    conn = connect_db(DB1_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM users;")  # Clear old data
    for i in range(1, 101):
        cursor.execute("INSERT INTO users (name) VALUES (%s);", (f"User {i}",))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Inserted 100 rows into db1")

def sync_data():
    #Sync data from db1 to db2 without duplication
    print("Sync Starting")
    conn1 = connect_db(DB1_CONFIG)
    conn2 = connect_db(DB2_CONFIG)
    cursor1 = conn1.cursor()
    cursor2 = conn2.cursor()

    # Ensure 'users' table exists in db2
    cursor2.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        );
    """)

    # Clear existing data in db2 to prevent duplicates
    cursor2.execute("DELETE FROM users;")

    # Fetch all rows from db1 and insert into db2
    cursor1.execute("SELECT * FROM users;")
    rows = cursor1.fetchall()

    # Insert rows into db2 with conflict handling
    cursor2.executemany("INSERT INTO users (id, name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING;", rows)

    conn2.commit()
    cursor1.close()
    cursor2.close()
    conn1.close()
    conn2.close()
    print("Synchronized data from db1 to db2")

def get_table_hash(cursor, table_name):
    #Compute a hashset of the entire table to verify row integrity
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY id;")
    rows = cursor.fetchall()
    
    # Convert each row to a hashable string and compute a cumulative hash
    hash_obj = hashlib.sha256()
    for row in rows:
        hash_obj.update(str(row).encode())  # Encoding to bytes
    
    return hash_obj.hexdigest()  # Return unique hash of the table

def show_first_5_rows():
    #Fetch and display the first 5 rows from both db1 and db2
    conn1 = connect_db(DB1_CONFIG)
    conn2 = connect_db(DB2_CONFIG)
    cursor1 = conn1.cursor()
    cursor2 = conn2.cursor()

    print("\n First 5 rows from db1:")
    cursor1.execute("SELECT * FROM users ORDER BY id LIMIT 5;")
    rows1 = cursor1.fetchall()
    for row in rows1:
        print(row)

    print("\n First 5 rows from db2:")
    cursor2.execute("SELECT * FROM users ORDER BY id LIMIT 5;")
    rows2 = cursor2.fetchall()
    for row in rows2:
        print(row)

    cursor1.close()
    cursor2.close()
    conn1.close()
    conn2.close()

def verify_sync():
    #Step 1: Verify row count, Step 2: Verify hash of both tables
    
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
        print(f"Row count matches: {count1} rows in both db1 and db2")
    else:
        print(f"Row count mismatch: db1 has {count1}, db2 has {count2}")

    # Step 2: Verify data integrity using hash comparison
    hash1 = get_table_hash(cursor1, "users")
    hash2 = get_table_hash(cursor2, "users")

    if hash1 == hash2:
        print("Hash verification successful: Both tables have identical data")
    else:
        print("Hash mismatch: Data in db1 and db2 are different")

    # Close connections
    cursor1.close()
    cursor2.close()
    conn1.close()
    conn2.close()

# Run full pipeline
time.sleep(5)  # Wait for databases to be ready
insert_data()
sync_data()
verify_sync()
show_first_5_rows()  # Display first 5 rows from both databases
