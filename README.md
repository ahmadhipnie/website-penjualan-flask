# Flask E-Commerce - Website Penjualan 🛒

Website e-commerce menggunakan Flask dan MySQL dengan template SB Admin 2. Project ini sudah menggunakan **Template Layout System** yang modular dan mudah dikembangkan.

## ✨ Fitur

### 🔐 Authentication & Authorization
- ✅ Sistem Login & Register
- ✅ Role-based Access Control (Admin & Customer)
- ✅ Session Management
- ✅ Flash Messages

### 👨‍💼 Admin Panel
- ✅ Dashboard Admin
- ✅ **Manajemen Produk** (CRUD dengan upload multiple gambar)
- ✅ **Manajemen Kategori** (CRUD)
- ✅ **Manajemen Jenis Ekspedisi** (CRUD)
- ✅ **Manajemen Transaksi** (Lihat, Detail, Update Status)
  - Update status: Diproses → Dikirim (dengan input ekspedisi & resi)
  - Update status: Dikirim → Sampai (dengan upload bukti foto)
  - Update status sederhana (Selesai, Dibatalkan)
- ✅ **Laporan Transaksi**
  - Filter berdasarkan status
  - Filter berdasarkan range tanggal
  - Export ke Excel (.xlsx)
  - Export ke PDF
  - Summary per status
  - Total transaksi & pendapatan

### 👤 Customer Panel
- ✅ Dashboard Customer
- ✅ Landing Page dengan katalog produk
- ✅ Lihat detail produk
- 🔄 Keranjang Belanja (In Progress)
- 🔄 Checkout & Pembayaran (In Progress)
- 🔄 Tracking Pesanan (In Progress)

### 🎨 UI/UX
- ✅ Template Layout System (Modular & Reusable)
- ✅ Responsive Design (Bootstrap 4)
- ✅ SB Admin 2 Theme
- ✅ DataTables untuk tabel interaktif
- ✅ Font Awesome Icons

## 🚀 Instalasi

### Prasyarat

- Python 3.8 atau lebih baru
- MySQL 8.0 atau lebih baru
- pip (Python package manager)

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd website_python_penjualan
```

### Step 2: Setup Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

#### Windows:

Jika mengalami error saat install `mysqlclient`, ada 2 opsi:

**Opsi A - Install Build Tools (Recommended):**
1. Download dan install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Pilih "Desktop development with C++"
3. Install
4. Restart terminal dan jalankan:
```bash
pip install -r requirements.txt
```

**Opsi B - Gunakan PyMySQL (Lebih Mudah):**
1. Edit `requirements.txt`:
   - Comment baris `mysqlclient>=2.2.0` (tambah # di depan)
   - Uncomment baris `PyMySQL>=1.1.0` (hapus # di depan)
2. Edit `model/database.py`, ganti baris pertama:
   ```python
   # Dari:
   import MySQLdb
   # Menjadi:
   import pymysql as MySQLdb
   ```
3. Install:
```bash
pip install -r requirements.txt
```

#### Linux (Ubuntu/Debian):

```bash
# Install dependencies sistem
sudo apt-get update
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential pkg-config

# Install Python packages
pip install -r requirements.txt
```

#### macOS:

```bash
# Install MySQL client
brew install mysql-client
export PATH="/usr/local/opt/mysql-client/bin:$PATH"

# Install Python packages
pip install -r requirements.txt
```

### Step 4: Setup Database

1. **Buat database di MySQL:**
```sql
CREATE DATABASE penjualan_flask CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. **Import schema database:**
```bash
# Menggunakan MySQL command line
mysql -u root -p penjualan_flask < penjualan_flask.sql

# Atau menggunakan phpMyAdmin:
# - Buka phpMyAdmin
# - Pilih database penjualan_flask
# - Import file penjualan_flask.sql
```

### Step 5: Konfigurasi Aplikasi

Edit file `main.py` sesuaikan dengan konfigurasi MySQL Anda:

```python
# Konfigurasi MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'          # Sesuaikan username MySQL
app.config['MYSQL_PASSWORD'] = ''          # Sesuaikan password MySQL
app.config['MYSQL_DB'] = 'penjualan_flask'
```

### Step 6: Jalankan Aplikasi

```bash
python main.py
```

Server akan berjalan di: `http://127.0.0.1:5000`

## 🔐 Login Default

Gunakan akun berikut untuk testing:

**Admin:**
- Email: `admin@furniturestore.com`
- Password: `password`

**Customer:**
- Email: `hypeniett@gmail.com`
- Password: `password`

## 📁 Struktur Folder

```
.
├── main.py                     # File utama Flask
├── requirements.txt            # Dependencies
├── penjualan_flask.sql        # Database schema
│
├── controller/                 # Controllers
│   ├── auth/
│   │   └── AuthController.py   # Login, Register, Logout
│   ├── admin/
│   │   ├── KategoriController.py
│   │   ├── ProdukController.py
│   │   ├── JenisEkspedisiController.py
│   │   ├── TransaksiController.py
│   │   └── LaporanController.py
│   ├── customer/
│   │   └── DashboardCustomerController.py
│   └── landing/
│       └── LandingController.py
│
├── model/                      # Models
│   ├── database.py            # Database connection helper
│   ├── User.py                # User CRUD operations
│   ├── Kategori.py            # Kategori model
│   ├── Produk.py              # Produk model
│   ├── JenisEkspedisi.py      # Jenis Ekspedisi model
│   ├── Transaksi.py           # Transaksi model
│   └── Laporan.py             # Laporan model
│
├── templates/                  # HTML Templates
│   ├── auth/                  # Authentication pages
│   │   ├── login.html
│   │   └── register.html
│   │
│   ├── admin/                 # Admin section
│   │   ├── layout/            # Reusable components
│   │   │   ├── base_admin.html
│   │   │   ├── sidebar_admin.html
│   │   │   ├── topbar_admin.html
│   │   │   └── footer_admin.html
│   │   ├── dashboard/
│   │   │   └── index.html
│   │   ├── kategori/
│   │   │   └── index.html
│   │   ├── produk/
│   │   │   ├── index.html
│   │   │   ├── tambah.html
│   │   │   └── edit.html
│   │   ├── jenis_ekspedisi/
│   │   │   └── index.html
│   │   ├── transaksi/
│   │   │   ├── index.html
│   │   │   ├── detail.html
│   │   │   ├── kirim.html
│   │   │   └── sampai.html
│   │   └── laporan/
│   │       └── index.html
│   │
│   ├── customer/              # Customer section
│   │   ├── layout/            # Reusable components
│   │   ├── dashboard/
│   │   └── ...
│   │
│   └── landing/               # Landing pages
│       ├── index.html
│       ├── detail.html
│       └── ...
│
├── static/                     # Static files
│   ├── assets_sb_admin/       # SB Admin 2 theme
│   │   ├── css/
│   │   ├── js/
│   │   ├── img/
│   │   └── vendor/
│   ├── assets_landing/        # Landing page assets
│   ├── gambar_produk/         # Upload folder - product images
│   └── gambar_bukti_sampai/   # Upload folder - delivery proof
│
└── docs/                       # Documentation
    └── TEMPLATE_LAYOUT_GUIDE.md   # Template system guide
```

## 🎨 Template Layout System

Project ini menggunakan **Template Layout System** yang modular. Untuk membuat halaman baru:

```html
{% extends 'admin/layout/base_admin.html' %}

{% block title %}Judul Halaman{% endblock %}

{% block page_heading %}
<h1 class="h3 mb-0 text-gray-800">Judul Halaman</h1>
{% endblock %}

{% block content %}
<!-- Konten halaman Anda -->
{% endblock %}
```

**Keuntungan:**
- ✅ Tidak perlu menulis ulang sidebar, topbar, footer
- ✅ Kode lebih modular dan mudah maintenance
- ✅ Konsistensi tampilan otomatis
- ✅ Cepat dalam pengembangan

Dokumentasi lengkap: [TEMPLATE_LAYOUT_GUIDE.md](TEMPLATE_LAYOUT_GUIDE.md)

## 🛠️ Teknologi

- **Backend:** Flask 2.3+ (Python Web Framework)
- **Database:** MySQL 8.0+ dengan MySQLdb connector
- **Frontend:** Bootstrap 4 (SB Admin 2 Template)
- **JavaScript:** jQuery 3.x, DataTables
- **Icons:** Font Awesome 5
- **Export:** XlsxWriter (Excel), FPDF (PDF)
- **File Upload:** Werkzeug secure_filename

## 🔧 Troubleshooting

### Error: `mysqlclient` gagal diinstall

**Solusi 1:** Gunakan PyMySQL (lihat Step 3 - Opsi B)

**Solusi 2 (Windows):** Install Visual C++ Build Tools

**Solusi 3 (Linux):** Install development packages
```bash
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
```

### Error: `'NoneType' object has no attribute 'cursor'`

**Penyebab:** Koneksi MySQL gagal

**Solusi:**
1. Pastikan MySQL server berjalan
2. Cek konfigurasi di `main.py` (username, password, database name)
3. Pastikan database `penjualan_flask` sudah dibuat dan diimport

### Error: Template not found

**Penyebab:** Struktur folder template salah

**Solusi:**
1. Pastikan folder `templates/` ada di root project
2. Jalankan aplikasi dari root folder (folder yang ada `main.py`)

### Port 5000 sudah digunakan

**Solusi:** Ubah port di `main.py`:
```python
app.run(debug=True, port=5001)  # Ganti ke port lain
```

## 📝 Development Guide

### Menambah Halaman Baru

1. Buat file template di folder yang sesuai
2. Extends dari base template (`base_admin.html` atau `base_customer.html`)
3. Tambahkan route di `main.py` atau buat Controller baru
4. Update sidebar untuk menambah menu link

Contoh route baru:

```python
@app.route('/admin/produk')
def admin_produk():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/produk/index.html')
```

### Menambah Model Baru

1. Buat file di folder `model/`
2. Import `get_db` dari `model.database`
3. Gunakan pattern yang sama seperti `User.py`

### Update Sidebar Menu

Edit file:
- Admin: `templates/admin/layout/sidebar_admin.html`
- Customer: `templates/customer/layout/sidebar_customer.html`

## 📚 Dokumentasi Tambahan

- [Template Layout Guide](TEMPLATE_LAYOUT_GUIDE.md) - Panduan lengkap template system
- [Database Schema](penjualan_flask.sql) - Struktur database

## 🤝 Contributing

1. Fork repository
2. Buat branch baru (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📄 License

Project ini dibuat untuk keperluan pembelajaran.

## 👥 Author

- **Erik** - Initial work

## 🙏 Acknowledgments

- [SB Admin 2](https://startbootstrap.com/theme/sb-admin-2) - Bootstrap Admin Template
- [Flask](https://flask.palletsprojects.com/) - Python Web Framework
- [Bootstrap](https://getbootstrap.com/) - CSS Framework

---

**Dibuat dengan ❤️ menggunakan Flask dan MySQL**
