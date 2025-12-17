from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from model.database import get_db
from model.Produk import Produk
import os
import uuid

produk_bp = Blueprint('produk', __name__)

# Konfigurasi upload
UPLOAD_FOLDER = 'static/gambar_produk'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload_file(file):
    """Save uploaded file dengan nama unique"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Ensure directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        file.save(filepath)
        return filename
    return None

@produk_bp.route('/admin/produk')
def index():
    """Halaman daftar produk"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Anda harus login sebagai admin', 'danger')
        return redirect(url_for('auth.login'))
    
    db = get_db()
    produk_model = Produk(db)
    produks = produk_model.get_all()
    
    return render_template('admin/produk/index.html', produks=produks, user=session)

@produk_bp.route('/admin/produk/tambah', methods=['GET', 'POST'])
def tambah():
    """Halaman tambah produk"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Anda harus login sebagai admin', 'danger')
        return redirect(url_for('auth.login'))
    
    db = get_db()
    produk_model = Produk(db)
    
    if request.method == 'POST':
        # Ambil data form
        data = {
            'id_kategori': request.form.get('id_kategori'),
            'nama_barang': request.form.get('nama_barang', '').strip(),
            'deskripsi': request.form.get('deskripsi', '').strip(),
            'harga': request.form.get('harga', 0),
            'stok': request.form.get('stok', 0)
        }
        
        # Validasi
        if not data['nama_barang']:
            flash('Nama produk harus diisi', 'danger')
            return redirect(url_for('produk.tambah'))
        
        try:
            # Simpan produk
            produk_id = produk_model.create(data)
            
            # Handle multiple file upload
            files = request.files.getlist('gambar[]')
            is_first = True
            uploaded_count = 0
            
            for file in files:
                if file and file.filename != '':
                    filename = save_upload_file(file)
                    if filename:
                        # Gambar pertama adalah primary
                        produk_model.add_image(produk_id, filename, 1 if is_first else 0)
                        is_first = False
                        uploaded_count += 1
            
            flash(f'Produk berhasil ditambahkan dengan {uploaded_count} gambar', 'success')
            return redirect(url_for('produk.index'))
            
        except Exception as e:
            flash(f'Gagal menambahkan produk: {str(e)}', 'danger')
            return redirect(url_for('produk.tambah'))
    
    # GET request - tampilkan form
    kategoris = produk_model.get_all_kategoris()
    return render_template('admin/produk/tambah.html', kategoris=kategoris, user=session)

@produk_bp.route('/admin/produk/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """Halaman edit produk"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Anda harus login sebagai admin', 'danger')
        return redirect(url_for('auth.login'))
    
    db = get_db()
    produk_model = Produk(db)
    produk = produk_model.get_by_id(id)
    
    if not produk:
        flash('Produk tidak ditemukan', 'danger')
        return redirect(url_for('produk.index'))
    
    if request.method == 'POST':
        # Ambil data form
        data = {
            'id_kategori': request.form.get('id_kategori'),
            'nama_barang': request.form.get('nama_barang', '').strip(),
            'deskripsi': request.form.get('deskripsi', '').strip(),
            'harga': request.form.get('harga', 0),
            'stok': request.form.get('stok', 0)
        }
        
        # Validasi
        if not data['nama_barang']:
            flash('Nama produk harus diisi', 'danger')
            return redirect(url_for('produk.edit', id=id))
        
        try:
            # Update produk
            produk_model.update(id, data)
            
            # Handle new images upload
            files = request.files.getlist('gambar[]')
            existing_images = produk_model.get_images(id)
            uploaded_count = 0
            
            for file in files:
                if file and file.filename != '':
                    filename = save_upload_file(file)
                    if filename:
                        # Jika belum ada gambar, set sebagai primary
                        is_primary = 1 if len(existing_images) == 0 and uploaded_count == 0 else 0
                        produk_model.add_image(id, filename, is_primary)
                        uploaded_count += 1
            
            if uploaded_count > 0:
                flash(f'Produk berhasil diupdate dengan {uploaded_count} gambar baru', 'success')
            else:
                flash('Produk berhasil diupdate', 'success')
            
            return redirect(url_for('produk.index'))
            
        except Exception as e:
            flash(f'Gagal mengupdate produk: {str(e)}', 'danger')
            return redirect(url_for('produk.edit', id=id))
    
    # GET request - tampilkan form
    kategoris = produk_model.get_all_kategoris()
    images = produk_model.get_images(id)
    
    return render_template('admin/produk/edit.html', 
                         produk=produk, 
                         kategoris=kategoris, 
                         images=images,
                         user=session)

@produk_bp.route('/admin/produk/delete/<int:id>', methods=['POST'])
def delete(id):
    """Menghapus produk"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_db()
    produk_model = Produk(db)
    
    try:
        # Get images first untuk delete files
        images = produk_model.get_images(id)
        
        # Delete produk (cascade akan delete gambar dari DB)
        success = produk_model.delete(id)
        
        if success:
            # Delete image files
            for img in images:
                filepath = os.path.join(UPLOAD_FOLDER, img['gambar_url'])
                if os.path.exists(filepath):
                    os.remove(filepath)
            
            return jsonify({'success': True, 'message': 'Produk berhasil dihapus'})
        else:
            return jsonify({'success': False, 'message': 'Produk tidak ditemukan'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Gagal menghapus produk: {str(e)}'}), 500

@produk_bp.route('/admin/produk/delete-image/<int:id>', methods=['POST'])
def delete_image(id):
    """Menghapus gambar produk"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_db()
    produk_model = Produk(db)
    
    try:
        filename = produk_model.delete_image(id)
        
        if filename:
            # Delete file
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return jsonify({'success': True, 'message': 'Gambar berhasil dihapus'})
        else:
            return jsonify({'success': False, 'message': 'Gambar tidak ditemukan'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Gagal menghapus gambar: {str(e)}'}), 500

@produk_bp.route('/admin/produk/set-primary/<int:produk_id>/<int:image_id>', methods=['POST'])
def set_primary(produk_id, image_id):
    """Set gambar sebagai gambar utama"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_db()
    produk_model = Produk(db)
    
    try:
        produk_model.set_primary_image(produk_id, image_id)
        return jsonify({'success': True, 'message': 'Gambar utama berhasil diset'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Gagal set gambar utama: {str(e)}'}), 500
