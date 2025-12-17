import os
from werkzeug.utils import secure_filename

class Produk:
    def __init__(self, db):
        self.db = db
    
    def get_all(self):
        """Mengambil semua produk dengan kategori dan gambar utama"""
        cursor = self.db.cursor()
        query = """
            SELECT 
                b.*,
                k.nama_kategori,
                (SELECT gambar_url FROM gambar_barangs WHERE id_barang = b.id AND is_primary = 1 LIMIT 1) as gambar_utama
            FROM barangs b
            LEFT JOIN kategoris k ON b.id_kategori = k.id
            ORDER BY b.id DESC
        """
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_by_id(self, produk_id):
        """Mengambil detail produk berdasarkan ID"""
        cursor = self.db.cursor()
        query = """
            SELECT b.*, k.nama_kategori
            FROM barangs b
            LEFT JOIN kategoris k ON b.id_kategori = k.id
            WHERE b.id = %s
        """
        cursor.execute(query, (produk_id,))
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def get_images(self, produk_id):
        """Mengambil semua gambar produk"""
        cursor = self.db.cursor()
        query = "SELECT * FROM gambar_barangs WHERE id_barang = %s ORDER BY is_primary DESC, id ASC"
        cursor.execute(query, (produk_id,))
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def create(self, data):
        """Menambahkan produk baru"""
        cursor = self.db.cursor()
        query = """
            INSERT INTO barangs (id_kategori, nama_barang, deskripsi, harga, stok, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        """
        cursor.execute(query, (
            data['id_kategori'],
            data['nama_barang'],
            data['deskripsi'],
            data['harga'],
            data['stok']
        ))
        self.db.commit()
        produk_id = cursor.lastrowid
        cursor.close()
        return produk_id
    
    def update(self, produk_id, data):
        """Mengupdate data produk"""
        cursor = self.db.cursor()
        query = """
            UPDATE barangs 
            SET id_kategori = %s, nama_barang = %s, deskripsi = %s, 
                harga = %s, stok = %s, updated_at = NOW()
            WHERE id = %s
        """
        cursor.execute(query, (
            data['id_kategori'],
            data['nama_barang'],
            data['deskripsi'],
            data['harga'],
            data['stok'],
            produk_id
        ))
        self.db.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        return affected_rows > 0
    
    def delete(self, produk_id):
        """Menghapus produk (cascade delete akan menghapus gambar)"""
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM barangs WHERE id = %s", (produk_id,))
        self.db.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        return affected_rows > 0
    
    def add_image(self, produk_id, filename, is_primary=0):
        """Menambahkan gambar produk"""
        cursor = self.db.cursor()
        query = """
            INSERT INTO gambar_barangs (id_barang, gambar_url, is_primary, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW())
        """
        cursor.execute(query, (produk_id, filename, is_primary))
        self.db.commit()
        image_id = cursor.lastrowid
        cursor.close()
        return image_id
    
    def delete_image(self, image_id):
        """Menghapus gambar produk"""
        cursor = self.db.cursor()
        # Get filename first untuk delete file
        cursor.execute("SELECT gambar_url FROM gambar_barangs WHERE id = %s", (image_id,))
        result = cursor.fetchone()
        
        if result:
            cursor.execute("DELETE FROM gambar_barangs WHERE id = %s", (image_id,))
            self.db.commit()
            cursor.close()
            return result['gambar_url']
        
        cursor.close()
        return None
    
    def set_primary_image(self, produk_id, image_id):
        """Set gambar sebagai gambar utama"""
        cursor = self.db.cursor()
        
        # Reset semua gambar produk menjadi bukan primary
        cursor.execute(
            "UPDATE gambar_barangs SET is_primary = 0 WHERE id_barang = %s",
            (produk_id,)
        )
        
        # Set gambar terpilih sebagai primary
        cursor.execute(
            "UPDATE gambar_barangs SET is_primary = 1 WHERE id = %s",
            (image_id,)
        )
        
        self.db.commit()
        cursor.close()
        return True
    
    def get_all_kategoris(self):
        """Mengambil semua kategori untuk dropdown"""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM kategoris ORDER BY nama_kategori ASC")
        result = cursor.fetchall()
        cursor.close()
        return result
