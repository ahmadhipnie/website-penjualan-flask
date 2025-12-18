from flask import Blueprint, render_template, session, redirect, url_for, request, g, jsonify
from functools import wraps
from model.database import get_db

customer_bp = Blueprint('customer', __name__)

def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'customer':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Context processor untuk menghitung jumlah item di keranjang
@customer_bp.context_processor
def inject_cart_count():
    cart_count = 0
    if 'user_id' in session and session.get('role') == 'customer':
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM keranjangs WHERE id_user = %s", (session['user_id'],))
            result = cursor.fetchone()
            cart_count = result['total'] if result else 0
            cursor.close()
        except Exception as e:
            # Jika terjadi error, set cart_count ke 0
            cart_count = 0
    return dict(cart_count=cart_count)

@customer_bp.route('/dashboard')
@customer_required
def dashboard():
    """Dashboard Customer"""
    db = get_db()
    cursor = db.cursor()
    
    # Hitung total pesanan
    cursor.execute("SELECT COUNT(*) as total FROM penjualans WHERE id_user = %s", (session['user_id'],))
    result = cursor.fetchone()
    total_pesanan = result['total'] if result else 0
    
    # Hitung pesanan selesai
    cursor.execute("SELECT COUNT(*) as total FROM penjualans WHERE id_user = %s AND status = 'selesai'", (session['user_id'],))
    result = cursor.fetchone()
    pesanan_selesai = result['total'] if result else 0
    
    # Hitung pesanan diproses (menunggu pembayaran + sedang diproses + dikirim)
    cursor.execute("""
        SELECT COUNT(*) as total FROM penjualans 
        WHERE id_user = %s AND status IN ('menunggu_pembayaran', 'sedang_diproses', 'dikirim')
    """, (session['user_id'],))
    result = cursor.fetchone()
    pesanan_diproses = result['total'] if result else 0
    
    # Hitung item di keranjang
    cursor.execute("SELECT COUNT(*) as total FROM keranjangs WHERE id_user = %s", (session['user_id'],))
    result = cursor.fetchone()
    keranjang_count = result['total'] if result else 0
    
    cursor.close()
    
    return render_template('customer/dashboard/index.html', 
                         user=session,
                         total_pesanan=total_pesanan,
                         pesanan_selesai=pesanan_selesai,
                         pesanan_diproses=pesanan_diproses,
                         keranjang_count=keranjang_count)

@customer_bp.route('/produk')
@customer_required
def produk():
    """Halaman Produk Customer"""
    db = get_db()
    cursor = db.cursor()
    
    # Ambil semua produk dari database
    cursor.execute("""
        SELECT b.*, k.nama_kategori, 
               (SELECT gambar_url FROM gambar_barangs WHERE id_barang = b.id AND is_primary = 1 LIMIT 1) as gambar_utama
        FROM barangs b 
        LEFT JOIN kategoris k ON b.id_kategori = k.id
        WHERE b.stok > 0
        ORDER BY b.created_at DESC
    """)
    produk_list = cursor.fetchall()
    cursor.close()
    
    return render_template('customer/produk/index.html', user=session, produk_list=produk_list)

@customer_bp.route('/keranjang')
@customer_required
def keranjang():
    """Halaman Keranjang Belanja"""
    db = get_db()
    cursor = db.cursor()
    
    # Ambil item keranjang user dengan detail produk
    cursor.execute("""
        SELECT k.id, k.id_user, k.id_barang, k.jumlah, k.created_at, k.updated_at,
               b.nama_barang, b.harga, b.stok,
               (SELECT gambar_url FROM gambar_barangs 
                WHERE id_barang = b.id AND is_primary = 1 LIMIT 1) as gambar_utama
        FROM keranjangs k
        JOIN barangs b ON k.id_barang = b.id
        WHERE k.id_user = %s
        ORDER BY k.created_at DESC
    """, (session['user_id'],))
    keranjang_items = cursor.fetchall()
    cursor.close()
    
    return render_template('customer/cart/index.html', user=session, keranjang_items=keranjang_items)

# Route katalog dihapus karena tidak digunakan lagi
# Menu customer hanya: Dashboard, Keranjang, Pesanan, Profil

@customer_bp.route('/pesanan')
@customer_required
def pesanan():
    """Halaman Pesanan Customer"""
    db = get_db()
    cursor = db.cursor()
    
    # Ambil semua pesanan customer
    cursor.execute("""
        SELECT p.id, p.id_user, p.id_jenis_ekspedisi, p.kode_transaksi,
               p.nomor_resi, p.alamat_pengiriman, 
               p.status, p.total_harga, 
               p.created_at, p.updated_at, je.nama_ekspedisi
        FROM penjualans p
        LEFT JOIN jenis_ekspedisis je ON p.id_jenis_ekspedisi = je.id
        WHERE p.id_user = %s
        ORDER BY p.created_at DESC
    """, (session['user_id'],))
    pesanan_list = cursor.fetchall()

    # Fetch detail items for each pesanan
    for pesanan in pesanan_list:
        cursor.execute("""
            SELECT dp.qty, dp.harga, dp.subtotal, b.nama_barang,
                   (SELECT gambar_url FROM gambar_barangs gb WHERE gb.id_barang = b.id AND gb.is_primary = 1 LIMIT 1) as gambar_utama
            FROM detail_penjualans dp
            JOIN barangs b ON dp.id_produk = b.id
            WHERE dp.id_penjualan = %s
        """, (pesanan['id'],))
        pesanan['items'] = cursor.fetchall()
    cursor.close()
    
    return render_template('customer/pesanan/index.html', user=session, pesanan_list=pesanan_list)

@customer_bp.route('/profil')
@customer_required
def profil():
    """Halaman Profil Customer"""
    db = get_db()
    cursor = db.cursor()
    
    # Ambil data user
    cursor.execute("""
        SELECT id, nama, email, nomor_telepon, tanggal_lahir, jenis_kelamin, 
               created_at, role, updated_at
        FROM users WHERE id = %s
    """, (session['user_id'],))
    user_data = cursor.fetchone()
    
    # Ambil alamat user
    cursor.execute("""
        SELECT id, alamat, provinsi, kabupaten, kecamatan, kode_pos, id_user
        FROM alamat_users WHERE id_user = %s
    """, (session['user_id'],))
    alamat_list = cursor.fetchall()
    cursor.close()
    
    return render_template('customer/profil/index.html', user=session, user_data=user_data, alamat_list=alamat_list)

@customer_bp.route('/alamat')
@customer_required
def alamat():
    """Halaman Alamat User"""
    db = get_db()
    cursor = db.cursor()
    
    # Ambil alamat user
    cursor.execute("""
        SELECT id, alamat, provinsi, kabupaten, kecamatan, kode_pos, id_user
        FROM alamat_users WHERE id_user = %s
    """, (session['user_id'],))
    alamat_list = cursor.fetchall()
    cursor.close()
    
    return render_template('customer/alamat_user/index.html', user=session, alamat_list=alamat_list)

# Route cart dihapus karena sudah digabung dengan keranjang
# Sekarang /keranjang dan /cart mengarah ke halaman yang sama

@customer_bp.route('/cart/update/<int:item_id>', methods=['POST'])
@customer_required
def cart_update(item_id):
    """Update jumlah item di keranjang"""
    try:
        jumlah = int(request.form.get('jumlah', 1))
        
        if jumlah < 1:
            return jsonify({'success': False, 'message': 'Jumlah minimal 1'})
        
        db = get_db()
        cursor = db.cursor()
        
        # Cek stok produk
        cursor.execute("""
            SELECT b.stok, b.harga 
            FROM keranjangs k 
            JOIN barangs b ON k.id_barang = b.id 
            WHERE k.id = %s AND k.id_user = %s
        """, (item_id, session['user_id']))
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            return jsonify({'success': False, 'message': 'Item tidak ditemukan'})
        
        stok = result['stok']
        harga = result['harga']
        
        if jumlah > stok:
            cursor.close()
            return jsonify({'success': False, 'message': 'Jumlah melebihi stok'})
        
        # Update jumlah
        cursor.execute("""
            UPDATE keranjangs 
            SET jumlah = %s, updated_at = NOW() 
            WHERE id = %s AND id_user = %s
        """, (jumlah, item_id, session['user_id']))
        db.commit()
        cursor.close()
        
        return jsonify({'success': True, 'harga': harga})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@customer_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@customer_required
def cart_remove(item_id):
    """Hapus item dari keranjang"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Hapus item
        cursor.execute("""
            DELETE FROM keranjangs 
            WHERE id = %s AND id_user = %s
        """, (item_id, session['user_id']))
        db.commit()
        cursor.close()
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@customer_bp.route('/profil/update', methods=['POST'])
@customer_required
def update_profil():
    """Update profil customer"""
    try:
        nama = request.form.get('nama')
        email = request.form.get('email')
        nomor_telepon = request.form.get('nomor_telepon')
        tanggal_lahir = request.form.get('tanggal_lahir')
        jenis_kelamin = request.form.get('jenis_kelamin')
        
        db = get_db()
        cursor = db.cursor()
        
        # Update data user
        cursor.execute("""
            UPDATE users 
            SET nama = %s, email = %s, nomor_telepon = %s, 
                tanggal_lahir = %s, jenis_kelamin = %s, updated_at = NOW()
            WHERE id = %s
        """, (nama, email, nomor_telepon, tanggal_lahir, jenis_kelamin, session['user_id']))
        
        db.commit()
        cursor.close()
        
        # Update session
        session['nama'] = nama
        session['email'] = email
        
        return jsonify({'success': True, 'message': 'Profil berhasil diupdate'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@customer_bp.route('/alamat/tambah', methods=['POST'])
@customer_required
def tambah_alamat():
    """Tambah alamat baru"""
    try:
        alamat = request.form.get('alamat')
        provinsi = request.form.get('provinsi')
        kabupaten = request.form.get('kabupaten')
        kecamatan = request.form.get('kecamatan')
        kode_pos = request.form.get('kode_pos')
        
        db = get_db()
        cursor = db.cursor()
        
        # Insert alamat baru
        cursor.execute("""
            INSERT INTO alamat_users (alamat, provinsi, kabupaten, kecamatan, kode_pos, id_user, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (alamat, provinsi, kabupaten, kecamatan, kode_pos, session['user_id']))
        
        db.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Alamat berhasil ditambahkan'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@customer_bp.route('/alamat/update/<int:alamat_id>', methods=['POST'])
@customer_required
def update_alamat(alamat_id):
    """Update alamat"""
    try:
        alamat = request.form.get('alamat')
        provinsi = request.form.get('provinsi')
        kabupaten = request.form.get('kabupaten')
        kecamatan = request.form.get('kecamatan')
        kode_pos = request.form.get('kode_pos')
        
        db = get_db()
        cursor = db.cursor()
        
        # Update alamat
        cursor.execute("""
            UPDATE alamat_users 
            SET alamat = %s, provinsi = %s, kabupaten = %s, 
                kecamatan = %s, kode_pos = %s, updated_at = NOW()
            WHERE id = %s AND id_user = %s
        """, (alamat, provinsi, kabupaten, kecamatan, kode_pos, alamat_id, session['user_id']))
        
        db.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Alamat berhasil diupdate'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@customer_bp.route('/alamat/delete/<int:alamat_id>', methods=['POST'])
@customer_required
def delete_alamat(alamat_id):
    """Hapus alamat"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Hapus alamat
        cursor.execute("""
            DELETE FROM alamat_users 
            WHERE id = %s AND id_user = %s
        """, (alamat_id, session['user_id']))
        
        db.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Alamat berhasil dihapus'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@customer_bp.route('/pesanan/konfirmasi/<int:penjualan_id>', methods=['POST'])
@customer_required
def konfirmasi_terima(penjualan_id):
    """Konfirmasi penerimaan barang oleh customer: ubah status 'sampai' -> 'selesai'"""
    try:
        db = get_db()
        cursor = db.cursor()
        # Pastikan pesanan ada dan milik user
        cursor.execute("SELECT id, id_user, status FROM penjualans WHERE id = %s", (penjualan_id,))
        p = cursor.fetchone()
        if not p:
            cursor.close()
            return jsonify({'success': False, 'message': 'Pesanan tidak ditemukan'}), 404
        if p['id_user'] != session['user_id']:
            cursor.close()
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        if p['status'] != 'sampai':
            cursor.close()
            return jsonify({'success': False, 'message': 'Pesanan tidak dalam status sampai'}), 400
        # Update status
        cursor.execute("UPDATE penjualans SET status = 'selesai', updated_at = NOW() WHERE id = %s", (penjualan_id,))
        db.commit()
        cursor.close()
        return jsonify({'success': True, 'message': 'Konfirmasi berhasil. Pesanan selesai.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

