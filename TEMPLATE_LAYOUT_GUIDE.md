# Template Layout System - Dokumentasi

## 📁 Struktur Template

### Admin Templates
```
templates/admin/
├── layout/
│   ├── base_admin.html      # Template utama (extends dari sini)
│   ├── sidebar_admin.html   # Komponen sidebar admin
│   ├── topbar_admin.html    # Komponen topbar admin
│   └── footer_admin.html    # Komponen footer admin
└── dashboard/
    └── index.html           # Contoh penggunaan template
```

### Customer Templates
```
templates/customer/
├── layout/
│   ├── base_customer.html      # Template utama (extends dari sini)
│   ├── sidebar_customer.html   # Komponen sidebar customer
│   ├── topbar_customer.html    # Komponen topbar customer
│   └── footer_customer.html    # Komponen footer customer
└── dashboard.html              # Contoh penggunaan template
```

## 🚀 Cara Menggunakan Template

### 1. Membuat Halaman Admin Baru

Buat file baru di folder `templates/admin/` misalnya `templates/admin/produk/index.html`:

```html
{% extends 'admin/layout/base_admin.html' %}

{% block title %}Manajemen Produk - Admin{% endblock %}

{% block page_heading %}
<div class="d-sm-flex align-items-center justify-content-between mb-4">
    <h1 class="h3 mb-0 text-gray-800">Manajemen Produk</h1>
    <a href="#" class="btn btn-primary">
        <i class="fas fa-plus"></i> Tambah Produk
    </a>
</div>
{% endblock %}

{% block content %}
<div class="card shadow mb-4">
    <div class="card-header py-3">
        <h6 class="m-0 font-weight-bold text-primary">Daftar Produk</h6>
    </div>
    <div class="card-body">
        <!-- Konten halaman produk di sini -->
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nama Produk</th>
                    <th>Harga</th>
                    <th>Aksi</th>
                </tr>
            </thead>
            <tbody>
                <!-- Data produk -->
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
```

### 2. Membuat Halaman Customer Baru

Buat file baru di folder `templates/customer/` misalnya `templates/customer/produk.html`:

```html
{% extends 'customer/layout/base_customer.html' %}

{% block title %}Produk - E-Commerce{% endblock %}

{% block page_heading %}
<div class="d-sm-flex align-items-center justify-content-between mb-4">
    <h1 class="h3 mb-0 text-gray-800">Daftar Produk</h1>
</div>
{% endblock %}

{% block content %}
<div class="row">
    {% for produk in produk_list %}
    <div class="col-md-4 mb-4">
        <div class="card">
            <img src="{{ produk.gambar }}" class="card-img-top" alt="{{ produk.nama }}">
            <div class="card-body">
                <h5 class="card-title">{{ produk.nama }}</h5>
                <p class="card-text">Rp {{ produk.harga }}</p>
                <a href="#" class="btn btn-primary">Beli Sekarang</a>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
```

## 🔧 Blocks Yang Tersedia

### Base Template menyediakan blocks berikut:

1. **`{% block title %}`** - Judul halaman (muncul di tab browser)
2. **`{% block extra_css %}`** - CSS tambahan khusus untuk halaman
3. **`{% block page_heading %}`** - Heading halaman (judul, tombol, breadcrumb, dll)
4. **`{% block content %}`** - Konten utama halaman
5. **`{% block extra_js %}`** - JavaScript tambahan khusus untuk halaman

### Contoh Penggunaan Extra CSS/JS:

```html
{% extends 'admin/layout/base_admin.html' %}

{% block extra_css %}
<link href="{{ url_for('static', filename='assets_sb_admin/vendor/datatables/dataTables.bootstrap4.min.css') }}" rel="stylesheet">
{% endblock %}

{% block content %}
<!-- Konten halaman -->
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='assets_sb_admin/vendor/datatables/jquery.dataTables.min.js') }}"></script>
<script src="{{ url_for('static', filename='assets_sb_admin/vendor/datatables/dataTables.bootstrap4.min.js') }}"></script>
<script>
    $(document).ready(function() {
        $('#dataTable').DataTable();
    });
</script>
{% endblock %}
```

## 📝 Modifikasi Komponen

### Mengubah Sidebar Admin

Edit file `templates/admin/layout/sidebar_admin.html`:

```html
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('admin.produk') }}">
        <i class="fas fa-fw fa-box"></i>
        <span>Produk</span>
    </a>
</li>
```

### Mengubah Sidebar Customer

Edit file `templates/customer/layout/sidebar_customer.html`:

```html
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('customer.produk') }}">
        <i class="fas fa-fw fa-shopping-bag"></i>
        <span>Produk</span>
    </a>
</li>
```

### Active Menu State

Sidebar sudah dilengkapi dengan active state detection menggunakan `request.endpoint`:

```html
<li class="nav-item {{ 'active' if request.endpoint == 'admin_dashboard' }}">
    <a class="nav-link" href="{{ url_for('admin_dashboard') }}">
        <i class="fas fa-fw fa-tachometer-alt"></i>
        <span>Dashboard</span>
    </a>
</li>
```

## ✨ Keuntungan Template System

1. **DRY (Don't Repeat Yourself)** - Tidak perlu menulis ulang sidebar, topbar, footer di setiap halaman
2. **Maintainability** - Perubahan pada sidebar/topbar/footer cukup dilakukan di satu tempat
3. **Consistency** - Semua halaman menggunakan layout yang sama
4. **Scalability** - Mudah menambahkan halaman baru
5. **Separation of Concerns** - Struktur template terpisah dari konten halaman

## 🔄 Flash Messages

Flash messages sudah terintegrasi di base template. Cara menggunakan di controller:

```python
from flask import flash

# Success message
flash('Data berhasil disimpan!', 'success')

# Error message
flash('Terjadi kesalahan!', 'danger')

# Warning message
flash('Perhatian: Stok hampir habis!', 'warning')

# Info message
flash('Data telah diupdate.', 'info')
```

## 📊 Session Data

Sidebar dan topbar mengakses data user dari session:

```python
# Di controller, set session setelah login:
session['user_id'] = user['id']
session['nama'] = user['nama']
session['email'] = user['email']
session['role'] = user['role']

# Di template, akses dengan:
{{ session.nama }}
{{ session.email }}
{{ session.role }}
```

## 🎨 Customization

### Menambah Custom CSS untuk Halaman Tertentu

```html
{% extends 'admin/layout/base_admin.html' %}

{% block extra_css %}
<style>
    .custom-card {
        border-left: 4px solid #4e73df;
    }
</style>
{% endblock %}
```

### Menambah Custom JavaScript untuk Halaman Tertentu

```html
{% block extra_js %}
<script>
    function confirmDelete(id) {
        if (confirm('Yakin ingin menghapus data ini?')) {
            window.location.href = '/admin/produk/delete/' + id;
        }
    }
</script>
{% endblock %}
```

## 🚀 Best Practices

1. **Gunakan blocks dengan tepat** - Jangan override blocks yang tidak perlu
2. **Pisahkan CSS/JS khusus** - Gunakan `extra_css` dan `extra_js` untuk file tambahan
3. **Konsisten dengan naming** - Gunakan naming convention yang sama untuk route dan file
4. **Update sidebar secara berkala** - Tambahkan menu baru saat membuat fitur baru
5. **Test responsive design** - Pastikan halaman responsive di semua device

---

**Dibuat untuk**: Website E-Commerce Flask  
**Tanggal**: 17 Desember 2025  
**Framework**: Flask + Jinja2 + Bootstrap (SB Admin 2)
