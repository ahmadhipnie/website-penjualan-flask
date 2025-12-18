from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from model.Transaksi import Transaksi
from model.JenisEkspedisi import JenisEkspedisi
from werkzeug.utils import secure_filename
import os
from datetime import datetime

transaksi_bp = Blueprint('transaksi', __name__, url_prefix='/admin/transaksi')

UPLOAD_FOLDER = 'static/gambar_bukti_sampai'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@transaksi_bp.route('/')
def index():
    """Menampilkan daftar semua transaksi"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    
    transaksis = Transaksi.get_all()
    return render_template('admin/transaksi/index.html', transaksis=transaksis, user=session)

@transaksi_bp.route('/detail/<int:id>')
def detail(id):
    """Menampilkan detail transaksi"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    
    transaksi = Transaksi.get_by_id(id)
    if not transaksi:
        flash('Transaksi tidak ditemukan', 'danger')
        return redirect(url_for('transaksi.index'))
    
    items = Transaksi.get_detail_items(id)
    return render_template('admin/transaksi/detail.html', transaksi=transaksi, items=items, user=session)

@transaksi_bp.route('/kirim/<int:id>', methods=['GET', 'POST'])
def kirim(id):
    """Form untuk mengubah status menjadi dikirim"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    
    transaksi = Transaksi.get_by_id(id)
    if not transaksi:
        flash('Transaksi tidak ditemukan', 'danger')
        return redirect(url_for('transaksi.index'))
    
    if request.method == 'POST':
        id_jenis_ekspedisi = request.form.get('id_jenis_ekspedisi')
        nomor_resi = request.form.get('nomor_resi')
        prakiraan_tanggal_sampai = request.form.get('prakiraan_tanggal_sampai')
        
        if not id_jenis_ekspedisi or not nomor_resi or not prakiraan_tanggal_sampai:
            flash('Semua field harus diisi', 'danger')
            return redirect(url_for('transaksi.kirim', id=id))
        
        try:
            Transaksi.update_to_dikirim(id, id_jenis_ekspedisi, nomor_resi, prakiraan_tanggal_sampai)
            flash('Status transaksi berhasil diubah menjadi Dikirim', 'success')
            return redirect(url_for('transaksi.detail', id=id))
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
            return redirect(url_for('transaksi.kirim', id=id))
    
    # GET request - tampilkan form
    jenis_ekspedisis = JenisEkspedisi.get_all()
    return render_template('admin/transaksi/kirim.html', transaksi=transaksi, jenis_ekspedisis=jenis_ekspedisis, user=session)

@transaksi_bp.route('/sampai/<int:id>', methods=['GET', 'POST'])
def sampai(id):
    """Form untuk mengubah status menjadi sampai dengan upload bukti"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    
    transaksi = Transaksi.get_by_id(id)
    if not transaksi:
        flash('Transaksi tidak ditemukan', 'danger')
        return redirect(url_for('transaksi.index'))
    
    if request.method == 'POST':
        if 'gambar_bukti_sampai' not in request.files:
            flash('Gambar bukti sampai harus diupload', 'danger')
            return redirect(url_for('transaksi.sampai', id=id))
        
        file = request.files['gambar_bukti_sampai']
        
        if file.filename == '':
            flash('Tidak ada file yang dipilih', 'danger')
            return redirect(url_for('transaksi.sampai', id=id))
        
        if file and allowed_file(file.filename):
            # Generate nama file unik
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"bukti_{id}_{timestamp}_{filename}"
            
            # Pastikan folder ada
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Simpan file
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            try:
                Transaksi.update_to_sampai(id, filename)
                flash('Status transaksi berhasil diubah menjadi Sampai', 'success')
                return redirect(url_for('transaksi.detail', id=id))
            except Exception as e:
                # Hapus file jika terjadi error database
                if os.path.exists(filepath):
                    os.remove(filepath)
                flash(f'Terjadi kesalahan: {str(e)}', 'danger')
                return redirect(url_for('transaksi.sampai', id=id))
        else:
            flash('Format file tidak valid. Gunakan png, jpg, jpeg, atau gif', 'danger')
            return redirect(url_for('transaksi.sampai', id=id))
    
    # GET request - tampilkan form
    return render_template('admin/transaksi/sampai.html', transaksi=transaksi, user=session)

@transaksi_bp.route('/update-status/<int:id>/<status>')
def update_status(id, status):
    """Update status transaksi (untuk status sederhana tanpa data tambahan)"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    
    valid_statuses = ['sedang_diproses', 'selesai', 'dibatalkan']
    if status not in valid_statuses:
        flash('Status tidak valid', 'danger')
        return redirect(url_for('transaksi.detail', id=id))
    
    try:
        Transaksi.update_status(id, status)
        flash(f'Status transaksi berhasil diubah menjadi {status.replace("_", " ").title()}', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('transaksi.detail', id=id))
