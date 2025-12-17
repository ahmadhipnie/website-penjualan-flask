import MySQLdb

try:
    # Test koneksi MySQL
    db = MySQLdb.connect(
        host="localhost",
        user="root",
        password="",
        database="penjualan_flask"
    )
    
    print("✓ Koneksi MySQL berhasil!")
    
    # Test query
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM users")
    result = cursor.fetchone()
    print(f"✓ Query berhasil! Total users: {result[0]}")
    
    cursor.close()
    db.close()
    
except Exception as e:
    print(f"✗ Error koneksi MySQL: {e}")
    print("\nPastikan:")
    print("1. MySQL service sedang berjalan")
    print("2. Database 'penjualan_flask' sudah dibuat")
    print("3. Username dan password MySQL sudah benar")
