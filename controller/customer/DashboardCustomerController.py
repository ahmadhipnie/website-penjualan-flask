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
    return render_template('customer/dashboard/index.html', user=session)

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
    """Halaman Katalog Produk (dulu keranjang)"""
    db = get_db()
    cursor = db.cursor()
    
    # Ambil semua produk yang tersedia dengan kategori dan gambar
    cursor.execute("""
        SELECT b.id, b.nama_barang, b.deskripsi, b.harga, b.stok, 
               b.created_at, b.updated_at, b.id_kategori,
               k.nama_kategori,
               (SELECT gambar_url FROM gambar_barangs 
                WHERE id_barang = b.id AND is_primary = 1 LIMIT 1) as gambar_utama
        FROM barangs b 
        LEFT JOIN kategoris k ON b.id_kategori = k.id
        WHERE b.stok > 0
        ORDER BY b.created_at DESC
    """)
    produk_list = cursor.fetchall()
    
    # Ambil semua kategori untuk filter
    cursor.execute("SELECT id, nama_kategori FROM kategoris ORDER BY nama_kategori")
    kategori_list = cursor.fetchall()
    
    cursor.close()
    
    return render_template('customer/keranjang/index.html', 
                         user=session, 
                         produk_list=produk_list,
                         kategori_list=kategori_list)

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

@customer_bp.route('/cart')
@customer_required
def cart():
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

