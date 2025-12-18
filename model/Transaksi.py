from model.database import get_db
from flask import g

class Transaksi:
    @staticmethod
    def get_all():
        """Mengambil semua data transaksi dengan join ke tabel users dan jenis_ekspedisis"""
        db = get_db()
        cursor = db.cursor()
        query = """
            SELECT p.*, u.nama as nama_customer, u.email, u.nomor_telepon,
                   je.nama_ekspedisi
            FROM penjualans p
            JOIN users u ON p.id_user = u.id
            LEFT JOIN jenis_ekspedisis je ON p.id_jenis_ekspedisi = je.id
            ORDER BY p.created_at DESC
        """
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    @staticmethod
    def get_by_id(transaksi_id):
        """Mengambil detail transaksi berdasarkan ID"""
        db = get_db()
        cursor = db.cursor()
        query = """
            SELECT p.*, u.nama as nama_customer, u.email, u.nomor_telepon,
                   je.nama_ekspedisi
            FROM penjualans p
            JOIN users u ON p.id_user = u.id
            LEFT JOIN jenis_ekspedisis je ON p.id_jenis_ekspedisi = je.id
            WHERE p.id = %s
        """
        cursor.execute(query, (transaksi_id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    @staticmethod
    def get_detail_items(transaksi_id):
        """Mengambil detail items dari transaksi"""
        db = get_db()
        cursor = db.cursor()
        query = """
            SELECT dp.*, b.nama_barang, gb.gambar_url
            FROM detail_penjualans dp
            JOIN barangs b ON dp.id_produk = b.id
            LEFT JOIN gambar_barangs gb ON b.id = gb.id_barang AND gb.is_primary = 1
            WHERE dp.id_penjualan = %s
        """
        cursor.execute(query, (transaksi_id,))
        result = cursor.fetchall()
        cursor.close()
        return result

    @staticmethod
    def update_to_dikirim(transaksi_id, id_jenis_ekspedisi, nomor_resi, prakiraan_tanggal_sampai):
        """Update status transaksi menjadi dikirim"""
        db = get_db()
        cursor = db.cursor()
        query = """
            UPDATE penjualans 
            SET status = 'dikirim',
                id_jenis_ekspedisi = %s,
                nomor_resi = %s,
                prakiraan_tanggal_sampai = %s,
                updated_at = NOW()
            WHERE id = %s
        """
        cursor.execute(query, (id_jenis_ekspedisi, nomor_resi, prakiraan_tanggal_sampai, transaksi_id))
        db.commit()
        cursor.close()

    @staticmethod
    def update_to_sampai(transaksi_id, gambar_bukti_sampai):
        """Update status transaksi menjadi sampai dengan bukti foto"""
        db = get_db()
        cursor = db.cursor()
        query = """
            UPDATE penjualans 
            SET status = 'sampai',
                gambar_bukti_sampai = %s,
                updated_at = NOW()
            WHERE id = %s
        """
        cursor.execute(query, (gambar_bukti_sampai, transaksi_id))
        db.commit()
        cursor.close()

    @staticmethod
    def update_status(transaksi_id, new_status):
        """Update status transaksi"""
        db = get_db()
        cursor = db.cursor()
        query = """
            UPDATE penjualans 
            SET status = %s,
                updated_at = NOW()
            WHERE id = %s
        """
        cursor.execute(query, (new_status, transaksi_id))
        db.commit()
        cursor.close()
