from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from model.database import get_db
from model.Kategori import Kategori

kategori_bp = Blueprint('kategori', __name__)

@kategori_bp.route('/admin/kategori')
def index():
    """Halaman daftar kategori"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Anda harus login sebagai admin', 'danger')
        return redirect(url_for('auth.login'))
    
    db = get_db()
    kategori_model = Kategori(db)
    kategoris = kategori_model.get_all()
    
    return render_template('admin/kategori/index.html', kategoris=kategoris, user=session)

@kategori_bp.route('/admin/kategori/store', methods=['POST'])
def store():
    """Menambahkan kategori baru"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    nama_kategori = request.form.get('nama_kategori', '').strip()
    
    # Validasi
    if not nama_kategori:
        return jsonify({'success': False, 'message': 'Nama kategori harus diisi'}), 400
    
    db = get_db()
    kategori_model = Kategori(db)
    
    # Cek duplikat
    if kategori_model.kategori_exists(nama_kategori):
        return jsonify({'success': False, 'message': 'Kategori sudah ada'}), 400
    
    try:
        kategori_id = kategori_model.create(nama_kategori)
        return jsonify({
            'success': True, 
            'message': 'Kategori berhasil ditambahkan',
            'kategori_id': kategori_id
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Gagal menambahkan kategori: {str(e)}'}), 500

@kategori_bp.route('/admin/kategori/get/<int:id>')
def get_kategori(id):
    """Mengambil data kategori untuk edit"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_db()
    kategori_model = Kategori(db)
    kategori = kategori_model.get_by_id(id)
    
    if kategori:
        return jsonify({
            'success': True,
            'data': {
                'id': kategori['id'],
                'nama_kategori': kategori['nama_kategori']
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Kategori tidak ditemukan'}), 404

@kategori_bp.route('/admin/kategori/update/<int:id>', methods=['POST'])
def update(id):
    """Mengupdate kategori"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    nama_kategori = request.form.get('nama_kategori', '').strip()
    
    # Validasi
    if not nama_kategori:
        return jsonify({'success': False, 'message': 'Nama kategori harus diisi'}), 400
    
    db = get_db()
    kategori_model = Kategori(db)
    
    # Cek apakah kategori exists
    existing = kategori_model.get_by_id(id)
    if not existing:
        return jsonify({'success': False, 'message': 'Kategori tidak ditemukan'}), 404
    
    try:
        success = kategori_model.update(id, nama_kategori)
        if success:
            return jsonify({
                'success': True,
                'message': 'Kategori berhasil diupdate'
            })
        else:
            return jsonify({'success': False, 'message': 'Gagal mengupdate kategori'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Gagal mengupdate kategori: {str(e)}'}), 500

@kategori_bp.route('/admin/kategori/delete/<int:id>', methods=['POST'])
def delete(id):
    """Menghapus kategori"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_db()
    kategori_model = Kategori(db)
    
    try:
        success = kategori_model.delete(id)
        if success:
            return jsonify({
                'success': True,
                'message': 'Kategori berhasil dihapus'
            })
        else:
            return jsonify({'success': False, 'message': 'Kategori tidak ditemukan'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Gagal menghapus kategori: {str(e)}'}), 500
