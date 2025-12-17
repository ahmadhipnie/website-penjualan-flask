# Flask E-Commerce - Website Penjualan

Website e-commerce menggunakan Flask dan MySQL dengan template SB Admin 2.

## Fitur
- Login & Register
- Dashboard Admin
- Dashboard Customer
- Manajemen Produk
- Keranjang Belanja
- Checkout & Pembayaran
- Tracking Pesanan

## Instalasi

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Setup Database:
- Buat database `penjualan_flask` di MySQL
- Import file `penjualan_flask.sql`

3. Konfigurasi Database:
Edit file `main.py` sesuaikan dengan konfigurasi MySQL Anda:
```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'penjualan_flask'
```

4. Pindahkan folder assets ke static:
```bash
# Pindahkan templates/assets_sb_admin ke static/assets_sb_admin
# Atau buat symlink
```

5. Jalankan aplikasi:
```bash
python main.py
```

6. Akses aplikasi:
```
http://localhost:5000
```

## Login Default

**Admin:**
- Email: admin@furniturestore.com
- Password: password

**Customer:**
- Email: hypeniett@gmail.com
- Password: password

## Struktur Folder

```
.
├── main.py                 # File utama Flask
├── controller/             # Controllers
│   ├── auth/              # Authentication controller
│   ├── admin/             # Admin controllers
│   └── customer/          # Customer controllers
├── model/                 # Models
│   └── User.py
├── templates/             # HTML templates
│   ├── auth/              # Login & Register
│   ├── admin/             # Admin pages
│   └── customer/          # Customer pages
├── static/                # Static files (CSS, JS, Images)
│   └── assets_sb_admin/   # SB Admin 2 assets
└── penjualan_flask.sql    # Database schema
```

## Teknologi
- Flask 3.0
- MySQL 8.0
- Bootstrap 4 (SB Admin 2)
- jQuery
