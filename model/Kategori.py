class Kategori:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        """Mengambil semua data kategori"""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM kategoris ORDER BY id DESC")
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_by_id(self, kategori_id):
        """Mengambil data kategori berdasarkan ID"""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM kategoris WHERE id = %s", (kategori_id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def create(self, nama_kategori):
        """Menambahkan kategori baru"""
        cursor = self.db.cursor()
        query = """
            INSERT INTO kategoris (nama_kategori, created_at, updated_at) 
            VALUES (%s, NOW(), NOW())
        """
        cursor.execute(query, (nama_kategori,))
        self.db.commit()
        kategori_id = cursor.lastrowid
        cursor.close()
        return kategori_id

    def update(self, kategori_id, nama_kategori):
        """Mengupdate data kategori"""
        cursor = self.db.cursor()
        query = """
            UPDATE kategoris 
            SET nama_kategori = %s, updated_at = NOW() 
            WHERE id = %s
        """
        cursor.execute(query, (nama_kategori, kategori_id))
        self.db.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        return affected_rows > 0

    def delete(self, kategori_id):
        """Menghapus kategori"""
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM kategoris WHERE id = %s", (kategori_id,))
        self.db.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        return affected_rows > 0

    def kategori_exists(self, nama_kategori):
        """Cek apakah nama kategori sudah ada"""
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM kategoris WHERE nama_kategori = %s", (nama_kategori,))
        result = cursor.fetchone()
        cursor.close()
        return result['count'] > 0
