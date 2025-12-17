from datetime import datetime

class JenisEkspedisi:
    def __init__(self, db):
        self.db = db
    
    def get_all(self):
        """Mengambil semua data jenis ekspedisi"""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM jenis_ekspedisis ORDER BY nama_ekspedisi ASC")
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_by_id(self, id):
        """Mengambil data jenis ekspedisi berdasarkan ID"""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM jenis_ekspedisis WHERE id = %s", (id,))
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def create(self, nama_ekspedisi):
        """Menambah jenis ekspedisi baru"""
        cursor = self.db.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "INSERT INTO jenis_ekspedisis (nama_ekspedisi, created_at, updated_at) VALUES (%s, %s, %s)",
            (nama_ekspedisi, now, now)
        )
        self.db.commit()
        cursor.close()
        return True
    
    def update(self, id, nama_ekspedisi):
        """Mengupdate jenis ekspedisi"""
        cursor = self.db.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "UPDATE jenis_ekspedisis SET nama_ekspedisi = %s, updated_at = %s WHERE id = %s",
            (nama_ekspedisi, now, id)
        )
        self.db.commit()
        cursor.close()
        return True
    
    def delete(self, id):
        """Menghapus jenis ekspedisi"""
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM jenis_ekspedisis WHERE id = %s", (id,))
        self.db.commit()
        cursor.close()
        return True
    
    def ekspedisi_exists(self, nama_ekspedisi, exclude_id=None):
        """Cek apakah nama ekspedisi sudah ada (untuk validasi duplikasi)"""
        cursor = self.db.cursor()
        if exclude_id:
            cursor.execute(
                "SELECT COUNT(*) as count FROM jenis_ekspedisis WHERE nama_ekspedisi = %s AND id != %s",
                (nama_ekspedisi, exclude_id)
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) as count FROM jenis_ekspedisis WHERE nama_ekspedisi = %s",
                (nama_ekspedisi,)
            )
        result = cursor.fetchone()
        cursor.close()
        return result['count'] > 0
