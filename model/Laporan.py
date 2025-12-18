from model.database import get_db

class Laporan:
    @staticmethod
    def get_transaksi_filtered(status=None, tanggal_dari=None, tanggal_sampai=None):
        """
        Mengambil data transaksi dengan filter
        
        Args:
            status: Status transaksi (optional)
            tanggal_dari: Tanggal mulai filter (optional)
            tanggal_sampai: Tanggal akhir filter (optional)
        """
        db = get_db()
        cursor = db.cursor()
        
        query = """
            SELECT p.*, u.nama as nama_customer, u.email, u.nomor_telepon,
                   je.nama_ekspedisi
            FROM penjualans p
            JOIN users u ON p.id_user = u.id
            LEFT JOIN jenis_ekspedisis je ON p.id_jenis_ekspedisi = je.id
            WHERE 1=1
        """
        
        params = []
        
        # Filter berdasarkan status
        if status and status != 'semua':
            query += " AND p.status = %s"
            params.append(status)
        
        # Filter berdasarkan tanggal
        if tanggal_dari:
            query += " AND DATE(p.created_at) >= %s"
            params.append(tanggal_dari)
        
        if tanggal_sampai:
            query += " AND DATE(p.created_at) <= %s"
            params.append(tanggal_sampai)
        
        query += " ORDER BY p.created_at DESC"
        
        cursor.execute(query, tuple(params))
        result = cursor.fetchall()
        cursor.close()
        return result

    @staticmethod
    def get_summary_by_status():
        """Mengambil ringkasan jumlah transaksi per status"""
        db = get_db()
        cursor = db.cursor()
        
        query = """
            SELECT status, COUNT(*) as jumlah, SUM(total_harga) as total
            FROM penjualans
            GROUP BY status
            ORDER BY status
        """
        
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    @staticmethod
    def get_detail_items_for_export(transaksi_ids):
        """Mengambil detail items untuk beberapa transaksi (untuk export)"""
        if not transaksi_ids:
            return []
        
        db = get_db()
        cursor = db.cursor()
        
        placeholders = ','.join(['%s'] * len(transaksi_ids))
        query = f"""
            SELECT dp.*, b.nama_barang, dp.id_penjualan
            FROM detail_penjualans dp
            JOIN barangs b ON dp.id_produk = b.id
            WHERE dp.id_penjualan IN ({placeholders})
        """
        
        cursor.execute(query, tuple(transaksi_ids))
        result = cursor.fetchall()
        cursor.close()
        return result
