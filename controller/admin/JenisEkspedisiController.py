from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from model.database import get_db
from model.JenisEkspedisi import JenisEkspedisi

jenis_ekspedisi_bp = Blueprint('jenis_ekspedisi', __name__)

@jenis_ekspedisi_bp.route('/admin/jenis-ekspedisi')
def index():
    """Menampilkan halaman daftar jenis ekspedisi"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Anda harus login sebagai admin', 'danger')
        return redirect(url_for('auth.login'))
    
    db = get_db()
    ekspedisi_model = JenisEkspedisi(db)
    ekspedisis = ekspedisi_model.get_all()
    return render_template('admin/jenis_ekspedisi/index.html', ekspedisis=ekspedisis, user=session)

@jenis_ekspedisi_bp.route('/admin/jenis-ekspedisi/store', methods=['POST'])
def store():
    """Menyimpan jenis ekspedisi baru"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    nama_ekspedisi = request.form.get('nama_ekspedisi', '').strip()
    
    if not nama_ekspedisi:
        return jsonify({
            'success': False,
            'message': 'Nama ekspedisi harus diisi!'
        }), 400
    
    db = get_db()
    ekspedisi_model = JenisEkspedisi(db)
    
    # Cek duplikasi
    if ekspedisi_model.ekspedisi_exists(nama_ekspedisi):
        return jsonify({
            'success': False,
            'message': 'Nama ekspedisi sudah ada!'
        }), 400
    
    try:
        ekspedisi_model.create(nama_ekspedisi)
        return jsonify({
            'success': True,
            'message': 'Jenis ekspedisi berhasil ditambahkan!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500

@jenis_ekspedisi_bp.route('/admin/jenis-ekspedisi/get/<int:id>')
def get_jenis_ekspedisi(id):
    """Mengambil data jenis ekspedisi untuk edit"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_db()
    ekspedisi_model = JenisEkspedisi(db)
    ekspedisi = ekspedisi_model.get_by_id(id)
    
    if ekspedisi:
        return jsonify({
            'success': True,
            'data': ekspedisi
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Data tidak ditemukan'
        }), 404

@jenis_ekspedisi_bp.route('/admin/jenis-ekspedisi/update/<int:id>', methods=['POST'])
def update(id):
    """Mengupdate jenis ekspedisi"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    nama_ekspedisi = request.form.get('nama_ekspedisi', '').strip()
    
    if not nama_ekspedisi:
        return jsonify({
            'success': False,
            'message': 'Nama ekspedisi harus diisi!'
        }), 400
    
    db = get_db()
    ekspedisi_model = JenisEkspedisi(db)
    
    # Cek apakah data ada
    ekspedisi = ekspedisi_model.get_by_id(id)
    if not ekspedisi:
        return jsonify({
            'success': False,
            'message': 'Data tidak ditemukan'
        }), 404
    
    # Cek duplikasi (kecuali data yang sedang diedit)
    if ekspedisi_model.ekspedisi_exists(nama_ekspedisi, id):
        return jsonify({
            'success': False,
            'message': 'Nama ekspedisi sudah ada!'
        }), 400
    
    try:
        ekspedisi_model.update(id, nama_ekspedisi)
        return jsonify({
            'success': True,
            'message': 'Jenis ekspedisi berhasil diupdate!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500

@jenis_ekspedisi_bp.route('/admin/jenis-ekspedisi/delete/<int:id>', methods=['POST'])
def delete(id):
    """Menghapus jenis ekspedisi"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_db()
    ekspedisi_model = JenisEkspedisi(db)
    
    # Cek apakah data ada
    ekspedisi = ekspedisi_model.get_by_id(id)
    if not ekspedisi:
        return jsonify({
            'success': False,
            'message': 'Data tidak ditemukan'
        }), 404
    
    try:
        ekspedisi_model.delete(id)
        return jsonify({
            'success': True,
            'message': 'Jenis ekspedisi berhasil dihapus!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500
