# Panduan Penggunaan Website E-Commerce Flask

## 🚀 Instalasi & Setup

### 1. Persiapan Database

Pastikan MySQL sudah terinstall dan berjalan di komputer Anda.

```bash
# Buat database
mysql -u root -p
CREATE DATABASE penjualan_flask;
exit;

# Import database schema
mysql -u root -p penjualan_flask < penjualan_flask.sql
```

### 2. Instalasi Dependencies

```bash
pip install -r requirements.txt
```

Dependencies yang diinstall:
- Flask 3.0.0 - Web framework
- Flask-MySQLdb 2.0.0 - MySQL connector
- mysqlclient 2.2.0 - MySQL driver
- Werkzeug 3.0.1 - Security utilities

### 3. Konfigurasi Database

Edit file `main.py` pada bagian konfigurasi MySQL:

```python
app.config['MYSQL_HOST'] = 'localhost'      # Host MySQL Anda
app.config['MYSQL_USER'] = 'root'           # Username MySQL
app.config['MYSQL_PASSWORD'] = ''           # Password MySQL
app.config['MYSQL_DB'] = 'penjualan_flask'  # Nama database
```

### 4. Jalankan Aplikasi

```bash
python main.py
```

Aplikasi akan berjalan di: **http://localhost:5000**

---

## 📝 Fitur yang Sudah Dibuat

### ✅ Authentication System

#### Login
- URL: `/auth/login`
- Field: Email, Password
- Validasi input
- Flash messages untuk error/success
- Session management
- Redirect berdasarkan role (admin/customer)

#### Register
- URL: `/auth/register`
- Field sesuai tabel users:
  - Nama Lengkap
  - Email
  - Nomor Telepon
  - Tanggal Lahir
  - Jenis Kelamin (L/P)
  - Password
  - Konfirmasi Password
- Validasi:
  - Semua field harus diisi
  - Email belum terdaftar
  - Password minimal 6 karakter
  - Password dan konfirmasi harus sama
- Password hashing menggunakan Werkzeug

#### Logout
- URL: `/auth/logout`
- Membersihkan session
- Redirect ke halaman login

---

## 🗂️ Struktur Project

```
website_python_penjualan/
│
├── main.py                      # Flask app utama
├── requirements.txt             # Dependencies
├── README.md                    # Dokumentasi
├── USAGE.md                     # Panduan ini
├── .env.example                 # Template environment variables
├── .gitignore                   # Git ignore file
├── penjualan_flask.sql          # Database schema
│
├── controller/                  # Controllers
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   └── AuthController.py   # Login, Register, Logout
│   ├── admin/
│   │   └── DashboardAdminController.py
│   └── customer/
│       └── DashboardAdminController.py
│
├── model/                       # Models
│   ├── __init__.py
│   └── User.py                 # User model dengan CRUD
│
├── templates/                   # HTML Templates
│   ├── auth/
│   │   ├── login.html          # ✅ Halaman login
│   │   └── register.html       # ✅ Halaman register
│   ├── admin/
│   │   ├── dashboard/
│   │   ├── laporan/
│   │   ├── produk/
│   │   └── transaksi/
│   ├── customer/
│   │   ├── alamat_user/
│   │   ├── layout/
│   │   ├── pesanan/
│   │   └── profil/
│   └── landing/
│       ├── cart.html
│       ├── checkout.html
│       ├── detail.html
│       └── index.html
│
└── static/                      # Static files
    └── assets_sb_admin/         # SB Admin 2 theme
        ├── css/
        ├── js/
        ├── img/
        └── vendor/
```

---

## 🔐 Login Default

Untuk testing, gunakan akun yang sudah ada di database:

**Admin:**
- Email: `admin@furniturestore.com`
- Password: `password`

**Customer:**
- Email: `hypeniett@gmail.com`
- Password: `password`

Atau daftar akun baru melalui halaman register.

---

## 💻 User Model - Methods

File: `model/User.py`

### `create_user(nama, email, nomor_telepon, tanggal_lahir, jenis_kelamin, password, role='customer')`
Membuat user baru dengan password hashing otomatis.

### `get_user_by_email(email)`
Mendapatkan data user berdasarkan email.

### `get_user_by_id(user_id)`
Mendapatkan data user berdasarkan ID.

### `verify_password(email, password)`
Verifikasi login user (support plain text dan hashed password).

### `email_exists(email)`
Cek apakah email sudah terdaftar.

### `update_user(user_id, data)`
Update data user (kecuali password).

---

## 🎨 Template & Assets

### Template Engine
- Jinja2 (bawaan Flask)
- Support untuk `{% %}` blocks, `{{ }}` variables, `{% if %}` conditionals

### Assets Location
- **Static files**: `static/assets_sb_admin/`
- **Usage**: `{{ url_for('static', filename='assets_sb_admin/css/sb-admin-2.min.css') }}`

### Bootstrap Theme
- SB Admin 2 (Bootstrap 4)
- Responsive design
- Custom components

---

## 📋 Database Schema

### Tabel Users
```sql
- id (bigint, PK, auto_increment)
- nama (varchar)
- email (varchar, unique)
- nomor_telepon (varchar)
- tanggal_lahir (date)
- jenis_kelamin (enum: 'L', 'P')
- password (varchar, hashed)
- role (enum: 'admin', 'customer')
- created_at (timestamp)
- updated_at (timestamp)
```

### Tabel Lainnya
- `alamat_users` - Alamat pengiriman user
- `kategoris` - Kategori produk
- `barangs` - Data produk
- `gambar_barangs` - Gambar produk
- `keranjangs` - Keranjang belanja
- `jenis_ekspedisis` - Jenis pengiriman
- `penjualans` - Data transaksi
- `detail_penjualans` - Detail item transaksi

---

## 🔧 Session Management

Session disimpan menggunakan Flask session dengan secret key random.

**Data yang disimpan di session saat login:**
```python
session['user_id']    # ID user
session['nama']       # Nama lengkap
session['email']      # Email
session['role']       # Role (admin/customer)
```

**Cek login:**
```python
if 'user_id' in session:
    # User sudah login
```

**Cek role:**
```python
if session.get('role') == 'admin':
    # User adalah admin
```

---

## 🚦 Routing

### Public Routes
- `/` - Redirect ke dashboard atau login
- `/auth/login` - Halaman login
- `/auth/register` - Halaman register

### Protected Routes
- `/admin/dashboard` - Dashboard admin (requires admin role)
- `/customer/dashboard` - Dashboard customer (requires customer role)
- `/auth/logout` - Logout

---

## 📱 Next Steps - Fitur yang Perlu Dibuat

### 1. Dashboard Admin
- [ ] Statistik penjualan
- [ ] Grafik revenue
- [ ] Produk terlaris
- [ ] User management

### 2. Manajemen Produk (Admin)
- [ ] List produk
- [ ] Tambah produk
- [ ] Edit produk
- [ ] Hapus produk
- [ ] Upload gambar produk
- [ ] Manajemen kategori

### 3. Dashboard Customer
- [ ] Profil user
- [ ] Riwayat pesanan
- [ ] Wishlist
- [ ] Notifikasi

### 4. Landing Page
- [ ] Katalog produk
- [ ] Filter & search
- [ ] Detail produk
- [ ] Review produk

### 5. Shopping Cart
- [ ] Tambah ke keranjang
- [ ] Update quantity
- [ ] Hapus item
- [ ] Checkout

### 6. Checkout & Payment
- [ ] Form alamat pengiriman
- [ ] Pilih ekspedisi
- [ ] Ringkasan order
- [ ] Integrasi payment gateway (Midtrans)

### 7. Order Management
- [ ] List pesanan
- [ ] Detail pesanan
- [ ] Update status
- [ ] Upload nomor resi
- [ ] Konfirmasi terima barang

---

## 🐛 Troubleshooting

### Error: "No module named 'MySQLdb'"
```bash
pip install mysqlclient
# Atau
pip install Flask-MySQLdb
```

### Error: "Access denied for user"
Periksa konfigurasi MySQL di `main.py`:
- Host, user, password harus benar
- Database sudah dibuat
- User punya akses ke database

### Assets tidak loading (404)
Pastikan folder `static/assets_sb_admin/` ada dan berisi semua file.

### Session tidak tersimpan
Pastikan `app.secret_key` sudah diset di `main.py`.

---

## 📚 Referensi

- Flask Documentation: https://flask.palletsprojects.com/
- Flask-MySQLdb: https://flask-mysqldb.readthedocs.io/
- SB Admin 2: https://startbootstrap.com/theme/sb-admin-2
- Jinja2 Template: https://jinja.palletsprojects.com/

---

Dibuat dengan ❤️ menggunakan Flask
