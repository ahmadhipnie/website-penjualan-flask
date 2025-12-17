from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from model.database import get_db
import requests
import json
from datetime import datetime
from config import midtrans

landing_bp = Blueprint('landing', __name__)

@landing_bp.route('/')
def index():
    """Landing page dengan kategori dan produk dari database"""
    db = get_db()
    cursor = db.cursor()
    
    # Ambil semua kategori
    cursor.execute("SELECT * FROM kategoris ORDER BY nama_kategori ASC")
    kategoris = cursor.fetchall()
    
    # Ambil produk dengan filter kategori jika ada
    kategori_id = request.args.get('kategori', type=int)
    
    if kategori_id:
        cursor.execute("""
            SELECT b.*, k.nama_kategori, gb.gambar_url
            FROM barangs b 
            LEFT JOIN kategoris k ON b.id_kategori = k.id 
            LEFT JOIN gambar_barangs gb ON b.id = gb.id_barang AND gb.is_primary = 1
            WHERE b.id_kategori = %s AND b.stok > 0
            ORDER BY b.created_at DESC
        """, (kategori_id,))
    else:
        cursor.execute("""
            SELECT b.*, k.nama_kategori, gb.gambar_url
            FROM barangs b 
            LEFT JOIN kategoris k ON b.id_kategori = k.id 
            LEFT JOIN gambar_barangs gb ON b.id = gb.id_barang AND gb.is_primary = 1
            WHERE b.stok > 0
            ORDER BY b.created_at DESC
        """)
    
    products = cursor.fetchall()
    
    cursor.close()
    
    return render_template('landing/index.html', 
                         kategoris=kategoris, 
                         products=products,
                         selected_kategori=kategori_id)

@landing_bp.route('/detail/<int:id>')
def detail(id):
    """Halaman detail produk"""
    db = get_db()
    cursor = db.cursor()
    
    # Ambil detail produk
    cursor.execute("""
        SELECT b.*, k.nama_kategori
        FROM barangs b
        LEFT JOIN kategoris k ON b.id_kategori = k.id
        WHERE b.id = %s
    """, (id,))
    product = cursor.fetchone()
    
    # Ambil semua gambar produk
    cursor.execute("""
        SELECT * FROM gambar_barangs 
        WHERE id_barang = %s 
        ORDER BY is_primary DESC, id ASC
    """, (id,))
    images = cursor.fetchall()
    
    # Ambil related products (produk lain dari kategori yang sama atau random)
    if product and product['id_kategori']:
        cursor.execute("""
            SELECT b.*, gb.gambar_url
            FROM barangs b
            LEFT JOIN gambar_barangs gb ON b.id = gb.id_barang AND gb.is_primary = 1
            WHERE b.id_kategori = %s AND b.id != %s AND b.stok > 0
            ORDER BY RAND()
            LIMIT 6
        """, (product['id_kategori'], id))
        related_products = cursor.fetchall()
    else:
        related_products = []
    
    cursor.close()
    
    return render_template('landing/detail.html', 
                         product=product,
                         images=images,
                         related_products=related_products)

@landing_bp.route('/cart')
def cart():
    """Halaman keranjang belanja"""
    # Redirect jika belum login
    if 'user_id' not in session or session.get('role') != 'customer':
        flash('Silakan login terlebih dahulu untuk melihat keranjang', 'warning')
        return redirect(url_for('auth.login'))
    
    db = get_db()
    cursor = db.cursor()
    
    # Ambil items di keranjang user dengan detail produk dan gambar
    cursor.execute("""
        SELECT k.id as keranjang_id, k.jumlah, k.id_barang,
               b.nama_barang, b.harga, b.stok,
               gb.gambar_url,
               (k.jumlah * b.harga) as subtotal
        FROM keranjangs k
        JOIN barangs b ON k.id_barang = b.id
        LEFT JOIN gambar_barangs gb ON b.id = gb.id_barang AND gb.is_primary = 1
        WHERE k.id_user = %s
        ORDER BY k.created_at DESC
    """, (session['user_id'],))
    cart_items = cursor.fetchall()
    
    # Hitung total
    total = sum(item['subtotal'] for item in cart_items)
    
    cursor.close()
    
    return render_template('landing/cart.html', 
                         cart_items=cart_items,
                         total=total)

@landing_bp.route('/cart/add', methods=['POST'])
def cart_add():
    """Tambah produk ke keranjang (AJAX)"""
    # Validasi login
    if 'user_id' not in session or session.get('role') != 'customer':
        return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu'}), 401
    
    try:
        data = request.get_json()
        id_barang = data.get('id_barang')
        quantity = int(data.get('quantity', 1))
        
        if not id_barang or quantity < 1:
            return jsonify({'success': False, 'message': 'Data tidak valid'}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Cek stok produk
        cursor.execute("SELECT stok, nama_barang FROM barangs WHERE id = %s", (id_barang,))
        product = cursor.fetchone()
        
        if not product:
            return jsonify({'success': False, 'message': 'Produk tidak ditemukan'}), 404
        
        # Cek apakah produk sudah ada di keranjang
        cursor.execute("""
            SELECT id, jumlah FROM keranjangs 
            WHERE id_user = %s AND id_barang = %s
        """, (session['user_id'], id_barang))
        existing_cart = cursor.fetchone()
        
        if existing_cart:
            # Update quantity
            new_quantity = existing_cart['jumlah'] + quantity
            
            # Validasi stok
            if new_quantity > product['stok']:
                return jsonify({
                    'success': False, 
                    'message': f'Stok tidak mencukupi. Maksimal {product["stok"]} pcs'
                }), 400
            
            cursor.execute("""
                UPDATE keranjangs SET jumlah = %s, updated_at = NOW() 
                WHERE id = %s
            """, (new_quantity, existing_cart['id']))
        else:
            # Validasi stok
            if quantity > product['stok']:
                return jsonify({
                    'success': False, 
                    'message': f'Stok tidak mencukupi. Maksimal {product["stok"]} pcs'
                }), 400
            
            # Insert baru
            cursor.execute("""
                INSERT INTO keranjangs (id_user, id_barang, jumlah, created_at, updated_at)
                VALUES (%s, %s, %s, NOW(), NOW())
            """, (session['user_id'], id_barang, quantity))
        
        db.commit()
        
        # Hitung total items di cart
        cursor.execute("""
            SELECT SUM(jumlah) as total_items 
            FROM keranjangs WHERE id_user = %s
        """, (session['user_id'],))
        cart_count = cursor.fetchone()['total_items'] or 0
        
        cursor.close()
        
        return jsonify({
            'success': True, 
            'message': f'{product["nama_barang"]} berhasil ditambahkan ke keranjang',
            'cart_count': cart_count
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@landing_bp.route('/cart/update/<int:id>', methods=['POST'])
def cart_update(id):
    """Update quantity item di keranjang"""
    if 'user_id' not in session or session.get('role') != 'customer':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        quantity = int(data.get('quantity', 1))
        
        if quantity < 1:
            return jsonify({'success': False, 'message': 'Quantity minimal 1'}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Ambil data keranjang dan stok produk
        cursor.execute("""
            SELECT k.id, k.id_barang, k.id_user, b.stok, b.nama_barang
            FROM keranjangs k
            JOIN barangs b ON k.id_barang = b.id
            WHERE k.id = %s
        """, (id,))
        cart_item = cursor.fetchone()
        
        if not cart_item:
            return jsonify({'success': False, 'message': 'Item tidak ditemukan'}), 404
        
        # Validasi owner
        if cart_item['id_user'] != session['user_id']:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Validasi stok
        if quantity > cart_item['stok']:
            return jsonify({
                'success': False, 
                'message': f'Stok tidak mencukupi. Maksimal {cart_item["stok"]} pcs'
            }), 400
        
        # Update quantity
        cursor.execute("""
            UPDATE keranjangs SET jumlah = %s, updated_at = NOW() 
            WHERE id = %s
        """, (quantity, id))
        
        db.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Quantity berhasil diupdate'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@landing_bp.route('/cart/remove/<int:id>', methods=['POST'])
def cart_remove(id):
    """Hapus item dari keranjang"""
    if 'user_id' not in session or session.get('role') != 'customer':
        flash('Silakan login terlebih dahulu', 'warning')
        return redirect(url_for('auth.login'))
    
    db = get_db()
    cursor = db.cursor()
    
    # Validasi ownership
    cursor.execute("SELECT id_user FROM keranjangs WHERE id = %s", (id,))
    cart_item = cursor.fetchone()
    
    if cart_item and cart_item['id_user'] == session['user_id']:
        cursor.execute("DELETE FROM keranjangs WHERE id = %s", (id,))
        db.commit()
        flash('Item berhasil dihapus dari keranjang', 'success')
    else:
        flash('Item tidak ditemukan', 'error')
    
    cursor.close()
    
    return redirect(url_for('landing.cart'))

@landing_bp.route('/cart/count')
def cart_count():
    """Get jumlah item di keranjang (untuk badge)"""
    if 'user_id' not in session or session.get('role') != 'customer':
        return jsonify({'count': 0})
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT SUM(jumlah) as total_items 
        FROM keranjangs WHERE id_user = %s
    """, (session['user_id'],))
    result = cursor.fetchone()
    
    cursor.close()
    
    return jsonify({'count': result['total_items'] or 0})

@landing_bp.route('/checkout')
def checkout():
    """Halaman checkout"""
    # Redirect jika belum login
    if 'user_id' not in session or session.get('role') != 'customer':
        flash('Silakan login terlebih dahulu', 'warning')
        return redirect(url_for('auth.login'))
    
    db = get_db()
    cursor = db.cursor()
    
    # Cek apakah cart kosong
    cursor.execute("""
        SELECT COUNT(*) as count FROM keranjangs WHERE id_user = %s
    """, (session['user_id'],))
    cart_count = cursor.fetchone()['count']
    
    if cart_count == 0:
        flash('Keranjang belanja Anda kosong', 'warning')
        return redirect(url_for('landing.cart'))
    
    # Ambil data user
    cursor.execute("""
        SELECT nama, email, nomor_telepon FROM users WHERE id = %s
    """, (session['user_id'],))
    user = cursor.fetchone()
    
    # Ambil cart items
    cursor.execute("""
        SELECT k.id as keranjang_id, k.jumlah, k.id_barang,
               b.nama_barang, b.harga, b.stok,
               gb.gambar_url,
               (k.jumlah * b.harga) as subtotal
        FROM keranjangs k
        JOIN barangs b ON k.id_barang = b.id
        LEFT JOIN gambar_barangs gb ON b.id = gb.id_barang AND gb.is_primary = 1
        WHERE k.id_user = %s
        ORDER BY k.created_at DESC
    """, (session['user_id'],))
    cart_items = cursor.fetchall()
    
    # Hitung total
    total = sum(item['subtotal'] for item in cart_items)
    
    # Ambil alamat user dari database
    cursor.execute("""
        SELECT id, alamat, provinsi, kabupaten, kecamatan, kode_pos 
        FROM alamat_users 
        WHERE id_user = %s 
        ORDER BY created_at DESC
    """, (session['user_id'],))
    alamat_list = cursor.fetchall()
    
    cursor.close()
    
    return render_template('landing/checkout.html',
                         user=user,
                         alamat_list=alamat_list,
                         cart_items=cart_items,
                         total=total)

@landing_bp.route('/checkout/process', methods=['POST'])
def checkout_process():
    """Process checkout dan generate Midtrans Snap Token"""
    if 'user_id' not in session or session.get('role') != 'customer':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        alamat_id = data.get('alamat_id')
        alamat_text = data.get('alamat_text')  # Full alamat string
        
        if not alamat_text:
            return jsonify({'success': False, 'message': 'Data tidak lengkap'}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Get cart items
        cursor.execute("""
            SELECT k.id_barang, k.jumlah, b.nama_barang, b.harga, b.stok,
                   (k.jumlah * b.harga) as subtotal
            FROM keranjangs k
            JOIN barangs b ON k.id_barang = b.id
            WHERE k.id_user = %s
        """, (session['user_id'],))
        cart_items = cursor.fetchall()
        
        if not cart_items:
            return jsonify({'success': False, 'message': 'Keranjang kosong'}), 400
        
        # Validasi stok
        for item in cart_items:
            if item['jumlah'] > item['stok']:
                return jsonify({
                    'success': False, 
                    'message': f'Stok {item["nama_barang"]} tidak mencukupi'
                }), 400
        
        # Calculate total
        total_harga = sum(item['subtotal'] for item in cart_items)
        
        # Generate kode transaksi
        kode_transaksi = f"TRX{datetime.now().strftime('%Y%m%d%H%M%S')}{session['user_id']}"
        
        # Get user data
        cursor.execute("SELECT nama, email, nomor_telepon FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        
        # Create Midtrans transaction
        snap_url = midtrans.SNAP_API_URL
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Basic {midtrans.MIDTRANS_SERVER_KEY}'
        }
        
        # Prepare transaction details
        transaction_details = {
            "transaction_details": {
                "order_id": kode_transaksi,
                "gross_amount": int(total_harga)
            },
            "customer_details": {
                "first_name": user['nama'],
                "email": user['email'],
                "phone": user['nomor_telepon'] or '08123456789'
            },
            "item_details": [
                {
                    "id": str(item['id_barang']),
                    "price": int(item['harga']),
                    "quantity": int(item['jumlah']),
                    "name": item['nama_barang']
                }
                for item in cart_items
            ]
        }
        
        # Request Snap Token from Midtrans
        import base64
        auth_string = base64.b64encode(midtrans.MIDTRANS_SERVER_KEY.encode()).decode()
        headers['Authorization'] = f'Basic {auth_string}'
        
        response = requests.post(snap_url, json=transaction_details, headers=headers)
        
        if response.status_code != 201:
            return jsonify({
                'success': False, 
                'message': 'Gagal membuat transaksi payment',
                'error': response.text
            }), 500
        
        snap_data = response.json()
        snap_token = snap_data.get('token')
        
        # Save to database
        cursor.execute("""
            INSERT INTO penjualans 
            (id_user, id_jenis_ekspedisi, kode_transaksi, snap_token, alamat_pengiriman, 
             status, total_harga, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (session['user_id'], None, kode_transaksi, snap_token, 
              alamat_text, 'menunggu_pembayaran', total_harga))
        
        penjualan_id = cursor.lastrowid
        
        # Save detail penjualan
        for item in cart_items:
            cursor.execute("""
                INSERT INTO detail_penjualans 
                (id_penjualan, id_produk, qty, harga, subtotal, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """, (penjualan_id, item['id_barang'], item['jumlah'], 
                  item['harga'], item['subtotal']))
        
        db.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'snap_token': snap_token,
            'order_id': kode_transaksi
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@landing_bp.route('/checkout/finish', methods=['POST'])
def checkout_finish():
    """Handle payment finish from frontend (alternative to webhook)"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        
        print(f"[CHECKOUT FINISH] Received order_id: {order_id}")
        
        if not order_id:
            print("[CHECKOUT FINISH] Error: Order ID tidak ditemukan")
            return jsonify({'success': False, 'message': 'Order ID tidak ditemukan'}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Get penjualan
        cursor.execute("""
            SELECT * FROM penjualans WHERE kode_transaksi = %s
        """, (order_id,))
        penjualan = cursor.fetchone()
        
        if not penjualan:
            print(f"[CHECKOUT FINISH] Error: Order {order_id} tidak ditemukan di database")
            return jsonify({'success': False, 'message': 'Order tidak ditemukan'}), 404
        
        print(f"[CHECKOUT FINISH] Found order: {penjualan['id']}, current status: {penjualan['status']}")
        
        # Check if already processed to prevent duplicate stock reduction
        if penjualan['status'] == 'sedang_diproses':
            print("[CHECKOUT FINISH] Order sudah diproses sebelumnya")
            cursor.close()
            return jsonify({'success': True, 'message': 'Order sudah diproses sebelumnya'}), 200
        
        # Update status to sedang_diproses
        cursor.execute("""
            UPDATE penjualans 
            SET status = 'sedang_diproses', updated_at = NOW()
            WHERE id = %s
        """, (penjualan['id'],))
        print(f"[CHECKOUT FINISH] Updated status to sedang_diproses")
        
        # Get detail penjualans
        cursor.execute("""
            SELECT id_produk, qty FROM detail_penjualans 
            WHERE id_penjualan = %s
        """, (penjualan['id'],))
        details = cursor.fetchall()
        
        print(f"[CHECKOUT FINISH] Found {len(details)} items to process")
        
        # Update stok
        for detail in details:
            cursor.execute("""
                UPDATE barangs 
                SET stok = stok - %s 
                WHERE id = %s
            """, (detail['qty'], detail['id_produk']))
            print(f"[CHECKOUT FINISH] Reduced stock for product {detail['id_produk']} by {detail['qty']}")
        
        # Clear cart
        cursor.execute("""
            DELETE FROM keranjangs WHERE id_user = %s
        """, (penjualan['id_user'],))
        print(f"[CHECKOUT FINISH] Cleared cart for user {penjualan['id_user']}")
        
        db.commit()
        cursor.close()
        
        print("[CHECKOUT FINISH] Success! All changes committed")
        return jsonify({'success': True, 'message': 'Pembayaran berhasil'}), 200
        
    except Exception as e:
        print(f"[CHECKOUT FINISH] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@landing_bp.route('/checkout/notification', methods=['POST'])
def checkout_notification():
    """Handle Midtrans payment notification (webhook)"""
    try:
        data = request.get_json()
        
        order_id = data.get('order_id')
        transaction_status = data.get('transaction_status')
        fraud_status = data.get('fraud_status', 'accept')
        
        db = get_db()
        cursor = db.cursor()
        
        # Get penjualan
        cursor.execute("""
            SELECT * FROM penjualans WHERE kode_transaksi = %s
        """, (order_id,))
        penjualan = cursor.fetchone()
        
        if not penjualan:
            return jsonify({'message': 'Order not found'}), 404
        
        # Update status based on transaction_status
        new_status = 'menunggu_pembayaran'
        
        if transaction_status == 'capture':
            if fraud_status == 'accept':
                new_status = 'sedang_diproses'
        elif transaction_status == 'settlement':
            new_status = 'sedang_diproses'
        elif transaction_status in ['deny', 'cancel', 'expire']:
            new_status = 'dibatalkan'
        elif transaction_status == 'pending':
            new_status = 'menunggu_pembayaran'
        
        # Update penjualan status
        cursor.execute("""
            UPDATE penjualans 
            SET status = %s, updated_at = NOW()
            WHERE id = %s
        """, (new_status, penjualan['id']))
        
        # Jika payment berhasil, kurangi stok dan clear cart (only if not already processed)
        if new_status == 'sedang_diproses' and penjualan['status'] != 'sedang_diproses':
            # Get detail penjualans
            cursor.execute("""
                SELECT id_produk, qty FROM detail_penjualans 
                WHERE id_penjualan = %s
            """, (penjualan['id'],))
            details = cursor.fetchall()
            
            # Update stok
            for detail in details:
                cursor.execute("""
                    UPDATE barangs 
                    SET stok = stok - %s 
                    WHERE id = %s
                """, (detail['qty'], detail['id_produk']))
            
            # Clear cart
            cursor.execute("""
                DELETE FROM keranjangs WHERE id_user = %s
            """, (penjualan['id_user'],))
        
        db.commit()
        cursor.close()
        
        return jsonify({'message': 'OK'}), 200
        
    except Exception as e:
        print(f"Error in notification: {str(e)}")
        return jsonify({'message': str(e)}), 500
