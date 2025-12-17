from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from model.User import User
from model.database import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validasi input
        if not email or not password:
            flash('Email dan password harus diisi!', 'danger')
            return render_template('auth/login.html')
        
        # Inisialisasi User model dengan koneksi database
        db = get_db()
        user_model = User(db)
        
        # Verifikasi user
        user = user_model.verify_password(email, password)
        
        if user:
            # Set session
            session['user_id'] = user['id']
            session['nama'] = user['nama']
            session['email'] = user['email']
            session['role'] = user['role']
            
            flash(f'Selamat datang, {user["nama"]}!', 'success')
            
            # Redirect berdasarkan role
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('customer.dashboard'))
        else:
            flash('Email atau password salah!', 'danger')
            return render_template('auth/login.html')
    
    # GET request - tampilkan form login
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Ambil data dari form
        nama = request.form.get('nama')
        email = request.form.get('email')
        nomor_telepon = request.form.get('nomor_telepon')
        tanggal_lahir = request.form.get('tanggal_lahir')
        jenis_kelamin = request.form.get('jenis_kelamin')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validasi input
        if not all([nama, email, nomor_telepon, tanggal_lahir, jenis_kelamin, password, confirm_password]):
            flash('Semua field harus diisi!', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Password dan konfirmasi password tidak cocok!', 'danger')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Password minimal 6 karakter!', 'danger')
            return render_template('auth/register.html')
        
        # Inisialisasi User model dengan koneksi database
        db = get_db()
        user_model = User(db)
        
        # Cek apakah email sudah terdaftar
        if user_model.email_exists(email):
            flash('Email sudah terdaftar!', 'danger')
            return render_template('auth/register.html')
        
        # Buat user baru
        if user_model.create_user(nama, email, nomor_telepon, tanggal_lahir, jenis_kelamin, password):
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Terjadi kesalahan saat registrasi. Silakan coba lagi.', 'danger')
            return render_template('auth/register.html')
    
    # GET request - tampilkan form register
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    # Hapus semua data session
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('auth.login'))
