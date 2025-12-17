from flask import Blueprint, render_template, session, redirect, url_for, request, g
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
    """Halaman Keranjang Customer"""
    db = get_db()
    cursor = db.cursor()
    
    # Ambil keranjang customer
    cursor.execute("""
        SELECT k.*, b.nama_barang, b.harga, b.stok,
               (SELECT gambar_url FROM gambar_barangs WHERE id_barang = b.id AND is_primary = 1 LIMIT 1) as gambar_utama
        FROM keranjangs k
        JOIN barangs b ON k.id_barang = b.id
        WHERE k.id_user = %s
    """, (session['user_id'],))
    keranjang_list = cursor.fetchall()
    cursor.close()
    
    return render_template('customer/keranjang/index.html', user=session, keranjang_list=keranjang_list)

@customer_bp.route('/pesanan')
@customer_required
def pesanan():
    """Halaman Pesanan Customer"""
    db = get_db()
    cursor = db.cursor()
    
    # Ambil semua pesanan customer
    cursor.execute("""
        SELECT p.*, je.nama_ekspedisi
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
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user_data = cursor.fetchone()
    
    # Ambil alamat user
    cursor.execute("SELECT * FROM alamat_users WHERE id_user = %s", (session['user_id'],))
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
    cursor.execute("SELECT * FROM alamat_users WHERE id_user = %s", (session['user_id'],))
    alamat_list = cursor.fetchall()
    cursor.close()
    
    return render_template('customer/alamat_user/index.html', user=session, alamat_list=alamat_list)
